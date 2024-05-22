import copy
import json
import logging
from datetime import datetime, timedelta

import requests
import towerlib
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import JSONField, ForeignKey, CASCADE, SET_NULL, DateTimeField, IntegerField, TextField, \
    OneToOneField, Q, PROTECT
from django.db.models.signals import post_save, pre_save
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django_fsm import transition, can_proceed, FSMIntegerField

from Squest.utils.ansible_when import AnsibleWhen
from Squest.utils.squest_model import SquestModel
from service_catalog.models.exceptions import ExceptionServiceCatalog
from service_catalog.models.hooks import HookManager
from service_catalog.models.instance import Instance, InstanceState
from service_catalog.models.operations import Operation, OperationType
from service_catalog.models.request_state import RequestState

logger = logging.getLogger(__name__)


class Request(SquestModel):
    class Meta:
        ordering = ["-last_updated"]
        permissions = [
            ("accept_request", "Can accept request"),
            ("cancel_request", "Can cancel request"),
            ("reject_request", "Can reject request"),
            ("archive_request", "Can archive request"),
            ("unarchive_request", "Can unarchive request"),
            ("re_submit_request", "Can re-submit request"),
            ("process_request", "Can process request"),
            ("hold_request", "Can hold request"),
            ("view_admin_survey", "Can view admin survey"),
            ("list_approvers", "Can view who can accept"),
        ]
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    fill_in_survey = JSONField(default=dict, blank=True)
    admin_fill_in_survey = JSONField(default=dict, blank=True)
    instance = ForeignKey(Instance, on_delete=CASCADE, null=True)
    operation = ForeignKey(Operation, on_delete=CASCADE)
    user = ForeignKey(User, blank=True, null=True, on_delete=PROTECT)
    date_submitted = DateTimeField(auto_now_add=True, blank=True, null=True)
    date_complete = DateTimeField(blank=True, null=True)
    date_archived = DateTimeField(blank=True, null=True)
    tower_job_id = IntegerField(blank=True, null=True)
    state = FSMIntegerField(default=RequestState.SUBMITTED, choices=RequestState.choices)
    periodic_task = ForeignKey(PeriodicTask, on_delete=SET_NULL, null=True, blank=True)
    periodic_task_date_expire = DateTimeField(auto_now=False, blank=True, null=True)
    failure_message = TextField(blank=True, null=True)
    accepted_by = ForeignKey(User, on_delete=PROTECT, blank=True, null=True, related_name="accepted_requests")
    processed_by = ForeignKey(User, on_delete=PROTECT, blank=True, null=True, related_name="processed_requests")
    approval_workflow_state = OneToOneField(
        "service_catalog.ApprovalWorkflowState",
        blank=True,
        null=True,
        on_delete=SET_NULL
    )

    @classmethod
    def get_q_filter(cls, user, perm):
        app_label, codename = perm.split(".")
        from profiles.models import GlobalScope
        ownerpermission = GlobalScope.load()
        additional_q = Q()
        if ownerpermission.owner_permissions.filter(
                codename=codename,
                content_type__app_label=app_label
        ).exists():
            additional_q = Q(user=user)

        return Q(
            instance__in=Instance.get_queryset_for_user(user, perm)
        ) | additional_q

    def is_owner(self, user):
        if self.user:
            return self.instance.is_owner(user) or self.user == user
        return self.instance.is_owner(user)

    def who_has_perm(self, permission_str):
        users = super().who_has_perm(permission_str)
        ## Permission give via GlobalScope.owner_permission
        from profiles.models import GlobalScope
        app_label, codename = permission_str.split(".")
        if GlobalScope.load().owner_permissions.filter(codename=codename, content_type__app_label=app_label).exists():
            if self.user:
                users = users | User.objects.filter(pk=self.user.pk).distinct()
            if self.instance.requester:
                users = users | User.objects.filter(pk=self.instance.requester.pk).distinct()
        return users

    def get_scopes(self):
        return self.instance.get_scopes()

    def __str__(self):
        return f"#{self.id}"

    def who_can_accept(self, exclude_superuser=False):
        if self.approval_workflow_state is not None:
            return self.approval_workflow_state.who_can_approve(exclude_superuser=exclude_superuser)
        else:
            return self.instance.quota_scope.who_has_perm("service_catalog.accept_request",
                                                          exclude_superuser=exclude_superuser)

    def full_survey_user(self, approval_step_state=None):

        if self.approval_workflow_state is not None and approval_step_state is not None:
            full_survey = dict()
            for tower_survey_field in approval_step_state.approval_step.editable_fields.all():
                if tower_survey_field.name in self.fill_in_survey:
                    full_survey.update(
                        {tower_survey_field.name: approval_step_state.fill_in_survey[tower_survey_field.name]})
        else:
            full_survey = {
                k: v for k, v in self.full_survey.items() if k in self.fill_in_survey
            }
        return full_survey

    @property
    def full_survey(self):
        # by default the survey is composed by what the end user provided
        full_survey = {k: v for k, v in {**self.fill_in_survey}.items() if v is not None}
        # when an approval workflow is used, we override with the content provided by each step
        if self.approval_workflow_state is not None:
            for step in self.approval_workflow_state.approval_step_states.all():
                full_survey.update(step.fill_in_survey)
        # the admin step always override what has been set in previous steps
        full_survey.update({k: v for k, v in {**self.admin_fill_in_survey}.items() if v is not None})
        return full_survey

    def clean(self):
        if self.fill_in_survey is None:
            raise ValidationError({'fill_in_survey': _("Please enter a valid JSON. Empty value is {} for JSON.")})

    def update_fill_in_surveys_accept_request(self, admin_provided_survey_fields):
        for key, value in admin_provided_survey_fields.items():
            if self.operation.tower_survey_fields.filter(is_customer_field=True, variable=key).exists():
                self.fill_in_survey[key] = value
            if self.operation.tower_survey_fields.filter(is_customer_field=False, variable=key).exists():
                self.admin_fill_in_survey[key] = value
        self.save()

    def can_process(self):
        if self.instance.state in [InstanceState.AVAILABLE, InstanceState.PENDING, InstanceState.UPDATE_FAILED,
                                   InstanceState.PROVISION_FAILED, InstanceState.DELETE_FAILED]:
            return True
        logger.debug(f"Request][process] instance {self.id} is not available or pending")
        return False

    # TODO: add the job id (url of tower and axw are different)
    @property
    def tower_job_url(self):
        return f"{self.operation.job_template.tower_server.url}/#/jobs/playbook/{self.tower_job_id}/output"

    @transition(field=state, source=RequestState.SUBMITTED, target=RequestState.ON_HOLD)
    def on_hold(self):
        pass

    @transition(field=state, source=[RequestState.SUBMITTED], target=RequestState.SUBMITTED)
    def re_submit(self, save=True):
        self.setup_approval_workflow()
        if save:
            self.save()

    @transition(field=state, source=[RequestState.SUBMITTED,
                                     RequestState.ON_HOLD,
                                     RequestState.REJECTED,
                                     RequestState.ACCEPTED], target=RequestState.CANCELED)
    def cancel(self):
        if self.instance.state == InstanceState.PENDING:
            self.instance.abort()
            self.instance.save()

    @transition(field=state, source=[RequestState.SUBMITTED, RequestState.ACCEPTED, RequestState.ON_HOLD],
                target=RequestState.REJECTED)
    def reject(self, user):
        if self.instance.state == InstanceState.PENDING:
            self.instance.abort()
            self.instance.save()
            return False
        return True

    @transition(field=state,
                source=[RequestState.ACCEPTED, RequestState.SUBMITTED, RequestState.FAILED, RequestState.ON_HOLD],
                target=RequestState.ACCEPTED)
    def accept(self, user, save=True):
        self.accepted_by = user
        self.state = RequestState.ACCEPTED
        if save:
            self.save()

    @transition(field=state, source=[RequestState.ACCEPTED, RequestState.FAILED], target=RequestState.PROCESSING,
                conditions=[can_process])
    def process(self, user=None, save=True):
        logger.info(f"[Request][process] trying to start processing request '{self.id}'")
        # the instance now switch depending on the operation type
        if self.operation.type == OperationType.CREATE:
            self.instance.provisioning()
        elif self.operation.type == OperationType.UPDATE:
            self.instance.updating()
        elif self.operation.type == OperationType.DELETE:
            self.instance.deleting()
        self.processed_by = user
        self.instance.save()
        if save:
            self.save()

    @transition(field=state, source=RequestState.PROCESSING)
    def perform_processing(self, inventory_override=None, credentials_override=None, tags_override=None,
                           skip_tags_override=None, limit_override=None, verbosity_override=None,
                           job_type_override=None, diff_mode_override=None):
        # get the survey with variables set by the end user and admin
        tower_extra_vars = copy.copy(self.full_survey)
        # add tower server extra vars
        tower_extra_vars.update(self.operation.job_template.tower_server.extra_vars)
        # add service extra vars
        tower_extra_vars.update(self.operation.service.extra_vars)
        # add operation extra vars
        tower_extra_vars.update(self.operation.extra_vars)
        # add the current instance to extra vars
        from service_catalog.api.serializers.request_serializers import AdminRequestSerializer
        from django.conf import settings
        tower_extra_vars["squest"] = {
            "squest_host": settings.SQUEST_HOST,
            "request": AdminRequestSerializer(self).data
        }
        tower_job_id = None
        try:
            tower_job_id, error_message = self.operation.job_template.execute(extra_vars=tower_extra_vars,
                                                                              inventory_override=inventory_override,
                                                                              credentials_override=credentials_override,
                                                                              tags_override=tags_override,
                                                                              skip_tags_override=skip_tags_override,
                                                                              limit_override=limit_override,
                                                                              verbosity_override=verbosity_override,
                                                                              job_type_override=job_type_override,
                                                                              diff_mode_override=diff_mode_override)
            # the execution could have failed directly because of missing variables
            if tower_job_id is None:
                self.has_failed(reason=error_message)
        except towerlib.towerlibexceptions.AuthFailed:
            self.has_failed(reason="towerlib.towerlibexceptions.AuthFailed")
        except requests.exceptions.SSLError:
            self.has_failed(reason="requests.exceptions.SSLError")
        except requests.exceptions.ConnectionError:
            self.has_failed(reason="requests.exceptions.ConnectionError")
        except ExceptionServiceCatalog.JobTemplateNotFound as e:
            self.has_failed(reason=e)
        except Exception as e:
            self.has_failed(reason=e)
        self.save()
        if isinstance(tower_job_id, int):
            self.tower_job_id = tower_job_id
            logger.info(f"[Request][process] process started on request '{self.id}'. Tower job id: {tower_job_id}")
            # create a periodic task to check the status until job is complete
            schedule, created = IntervalSchedule.objects.get_or_create(every=10,
                                                                       period=IntervalSchedule.SECONDS)
            self.periodic_task_date_expire = timezone.now() + timedelta(seconds=self.operation.process_timeout_second)
            self.periodic_task = PeriodicTask.objects.create(
                interval=schedule,
                name=f'job_status_check_request_{self.id}',
                task='service_catalog.tasks.check_tower_job_status_task',
                args=json.dumps([self.id]))
            logger.info(
                f'[Request][process] request \'{self.id}\': periodic task created. '
                f'Expire in {self.operation.process_timeout_second} seconds')

    @transition(field=state, source=RequestState.PROCESSING, target=RequestState.FAILED)
    def has_failed(self, reason=None):
        if reason is not None:
            self.failure_message = reason
        if self.operation.type == OperationType.CREATE:
            self.instance.provisioning_has_failed()
        elif self.operation.type == OperationType.UPDATE:
            self.instance.update_has_failed()
        elif self.operation.type == OperationType.DELETE:
            self.instance.delete_has_failed()
        self.instance.save()

    @transition(field=state, source=RequestState.PROCESSING, target=RequestState.COMPLETE)
    def complete(self):
        self.date_complete = datetime.now()

    @transition(field=state, source=RequestState.COMPLETE, target=RequestState.ARCHIVED)
    def archive(self):
        self.date_archived = datetime.now()

    @transition(field=state, source=RequestState.ARCHIVED, target=RequestState.COMPLETE)
    def unarchive(self):
        self.date_archived = None

    def delete(self, *args, **kwargs):
        if self.periodic_task is not None:
            self.periodic_task.delete()
        return super(self.__class__, self).delete(*args, **kwargs)

    def check_job_status(self):
        from ..mail_utils import send_mail_request_update
        if self.tower_job_id is None:
            logger.warning(
                f"[Request][check_job_status] no RHAAP/AWX job id for request id {self.id}. Check job status skipped")
            return

        # if the task is expired we remove the periodic task
        date_worker_now = timezone.now()
        if self.periodic_task_date_expire < date_worker_now:
            logger.info("[check_tower_job_status_task] request now expired. deleting the periodic task")
            self.has_failed(reason="Operation execution timeout")
            self.save()
            self.periodic_task.delete()
            return

        tower = self.operation.job_template.tower_server.get_tower_instance()
        job_object = tower.get_unified_job_by_id(self.tower_job_id)
        logger.info(f"[Request][check_job_status] status of Job #{self.tower_job_id}: {job_object.status}")
        if job_object.status == "successful":
            logger.info(f"[Request][check_job_status] RHAAP/AWX job status successful for request id {self.id}")
            self.complete()
            self.save()
            self.periodic_task.delete()
            if self.operation.type in [OperationType.CREATE, OperationType.UPDATE]:
                if self.operation.type == OperationType.CREATE:
                    self.instance.date_available = timezone.now()
                self.instance.available()
                self.instance.save()
            elif self.operation.type == OperationType.DELETE:
                self.instance.deleted()
                self.instance.save()
            # notify owner and admins that the request is complete
            send_mail_request_update(target_request=self)

        if job_object.status in ["canceled", "failed"]:
            error_message = f"RHAAP/AWX job {self.tower_job_id} status is '{job_object.status}'"
            self.has_failed(error_message)
            self.save()
            self.periodic_task.delete()
            send_mail_request_update(target_request=self)

    def _get_approval_workflow(self):
        from service_catalog.models import ApprovalWorkflow
        workflow = ApprovalWorkflow.objects.filter(
            enabled=True,
            operation=self.operation,
            scopes__id__in=[self.instance.quota_scope.id])
        if workflow.exists():
            return workflow.first()

        if self.instance.quota_scope.is_team:
            parent_workflow = ApprovalWorkflow.objects.filter(
                enabled=True,
                operation=self.operation,
                scopes__id__in=[self.instance.quota_scope.get_object().org.id]
            )
            if parent_workflow.exists():
                return parent_workflow.first()

        default_workflow = ApprovalWorkflow.objects.filter(enabled=True, operation=self.operation, scopes__isnull=True)
        if default_workflow.exists():
            return default_workflow.first()
        return None

    def setup_approval_workflow(self):
        if self.approval_workflow_state:
            self.approval_workflow_state.delete()
        # search for a workflow on this operation
        workflow = self._get_approval_workflow()
        if not workflow:
            logger.debug(f"Workflow not found for request #{self.id}")
            return
        logger.debug(f"Workflow found: {workflow.name} for request #{self.id}")
        # create pending steps
        self.approval_workflow_state = workflow.instantiate()
        self.save()

    def try_accept_current_step(self):
        if self.approval_workflow_state is not None \
                and self.approval_workflow_state.current_step is not None \
                and self.approval_workflow_state.current_step.approval_step.auto_accept_condition is not None:
            # test the condition
            from service_catalog.api.serializers import RequestSerializer
            context = {
                "request": RequestSerializer(self).data
            }
            if self.approval_workflow_state.current_step.approval_step.auto_accept_condition is not None:
                if AnsibleWhen.when_render(context=context,
                                           when_string=self.approval_workflow_state.current_step.approval_step.auto_accept_condition):
                    self.approval_workflow_state.approve_current_step()
                    if self.approval_workflow_state.current_step is not None:
                        self.try_accept_current_step()  # try again the new current step
                    else:
                        return True
        return False

    @classmethod
    def get_requests_awaiting_approval(cls, user):
        from profiles.models import Permission
        from service_catalog.models import ApprovalStepState
        all_requests = Request.objects.none()
        all_requests = all_requests | Request. \
            get_queryset_for_user(user, "service_catalog.accept_request"). \
            filter(state=RequestState.SUBMITTED).distinct()

        all_permissions_id = set(Permission.objects.filter(
            approval_step__approval_step_state__current_approval_workflow_state__request__state=RequestState.SUBMITTED
        ).values_list("id", flat=True))

        all_approval_step = ApprovalStepState.objects.none()
        for permission_id in all_permissions_id:
            permission = Permission.objects.get(id=permission_id)
            all_approval_step = all_approval_step | ApprovalStepState.get_queryset_for_user(user,
                                                                                            permission.permission_str) \
                .filter(current_approval_workflow_state__request__state=RequestState.SUBMITTED) \
                .distinct()

        all_requests = all_requests | Request.objects.filter(
            approval_workflow_state__current_step__in=all_approval_step).distinct()

        return all_requests

    @classmethod
    def auto_accept_and_process_signal(cls, sender, instance, created, *args, **kwargs):
        """
        Switch state to accept or process automatically if target operation auto_accept or auto_process is true
        when creating the Request
        :param instance: the current Request
        :type instance: Request
        """
        save_instance_on_update = False
        if instance.try_accept_current_step():
            save_instance_on_update = True
        else:
            if instance.operation.auto_accept:
                if instance.state == RequestState.SUBMITTED:
                    if can_proceed(instance.accept):
                        instance.accept(None, save=False)
                        save_instance_on_update = True
        if instance.operation.auto_process:
            if instance.state == RequestState.ACCEPTED:
                if can_proceed(instance.process):
                    instance.process(None, save=False)
                if can_proceed(instance.perform_processing):
                    instance.perform_processing()
                    save_instance_on_update = True
        if save_instance_on_update:
            instance.save()

    @classmethod
    def on_create(cls, sender, instance, created, *args, **kwargs):
        if created:
            # notify hook manager
            HookManager.trigger_hook(sender=sender, instance=instance, name="create_request", source="create",
                                     target=RequestState.SUBMITTED, *args, **kwargs)

            # create approval step if approval workflow is set
            instance.setup_approval_workflow()
            instance.try_accept_current_step()

    @classmethod
    def on_change(cls, sender, instance, *args, **kwargs):
        if instance.id is not None:
            previous = Request.objects.get(id=instance.id)
            if previous.state != instance.state:
                HookManager.trigger_hook(sender=sender, instance=instance, name="on_change_request",
                                         source=previous.state, target=instance.state,
                                         *args, **kwargs)


pre_save.connect(Request.on_change, sender=Request)
post_save.connect(Request.on_create, sender=Request)
post_save.connect(Request.auto_accept_and_process_signal, sender=Request)
