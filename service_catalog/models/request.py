import copy
import json
import logging
from datetime import datetime, timedelta

import requests
import towerlib
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import JSONField, ForeignKey, CASCADE, SET_NULL, DateTimeField, IntegerField, TextField, \
    OneToOneField, Q
from django.db.models.signals import post_save, pre_save
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django_fsm import FSMField, transition, post_transition, can_proceed

from Squest.utils.squest_model import SquestModel
from service_catalog.models.exceptions import ExceptionServiceCatalog
from service_catalog.models.instance import Instance, InstanceState
from service_catalog.models.operations import Operation, OperationType
from service_catalog.models.request_state import RequestState
from service_catalog.models.state_hooks import HookManager

logger = logging.getLogger(__name__)


class Request(SquestModel):
    class Meta:
        ordering = ["-date_submitted"]
        permissions = [
            ("accept_request", "Can accept request"),
            ("cancel_request", "Can cancel request"),
            ("reject_request", "Can reject request"),
            ("archive_request", "Can archive request"),
            ("unarchive_request", "Can unarchive request"),
            ("re_submit_request", "Can re-submit request"),
            ("process_request", "Can process request"),
            ("need_info_request", "Can ask info request"),
            ("view_admin_survey", "Can view admin survey"),
        ]
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    fill_in_survey = JSONField(default=dict, blank=True)
    admin_fill_in_survey = JSONField(default=dict, blank=True)
    instance = ForeignKey(Instance, on_delete=CASCADE, null=True)
    operation = ForeignKey(Operation, on_delete=CASCADE)
    user = ForeignKey(User, blank=True, null=True, on_delete=SET_NULL)
    date_submitted = DateTimeField(auto_now_add=True, blank=True, null=True)
    date_complete = DateTimeField(blank=True, null=True)
    date_archived = DateTimeField(blank=True, null=True)
    tower_job_id = IntegerField(blank=True, null=True)
    state = FSMField(default=RequestState.SUBMITTED, choices=RequestState.choices)
    periodic_task = ForeignKey(PeriodicTask, on_delete=SET_NULL, null=True, blank=True)
    periodic_task_date_expire = DateTimeField(auto_now=False, blank=True, null=True)
    failure_message = TextField(blank=True, null=True)
    accepted_by = ForeignKey(User, on_delete=SET_NULL, blank=True, null=True, related_name="accepted_requests")
    processed_by = ForeignKey(User, on_delete=SET_NULL, blank=True, null=True, related_name="processed_requests")
    approval_workflow_state = OneToOneField(
        "service_catalog.ApprovalWorkflowState",
        blank=True,
        null=True,
        on_delete=CASCADE
    )

    @classmethod
    def get_q_filter(cls, user, perm):
        return Q(
           instance__in=Instance.get_queryset_for_user(user, perm)
        )

    def get_scopes(self):
        return self.instance.get_scopes()

    def __str__(self):
        return f"#{self.id}"

    def full_survey_user(self, approval_step_state=None):

        if self.approval_workflow_state is not None and approval_step_state is not None:
            full_survey = dict()
            for tower_survey_field in approval_step_state.approval_step.editable_fields.all():
                if tower_survey_field.name in self.fill_in_survey:

                    full_survey.update({tower_survey_field.name: approval_step_state.fill_in_survey[tower_survey_field.name]})
        else:
            full_survey = {
                k: v for k, v in self.full_survey.items() if k in self.fill_in_survey
            }
        return full_survey

    @property
    def full_survey(self):
        # by default the survey is composed by what the end user provided, overriden by what the admin provided
        full_survey = {k: v for k, v in {**self.fill_in_survey, **self.admin_fill_in_survey}.items() if v is not None}
        # when an approval workflow is used, we override with the content provided by each step
        if self.approval_workflow_state is not None:
            for step in self.approval_workflow_state.approval_step_states.all():
                full_survey.update(step.fill_in_survey)
        return full_survey

    def clean(self):
        if self.fill_in_survey is None:
            raise ValidationError({'fill_in_survey': _("Please enter a valid JSON. Empty value is {} for JSON.")})

    def update_fill_in_surveys_accept_request(self, admin_provided_survey_fields):
        for key, value in admin_provided_survey_fields.items():
            if self.operation.tower_survey_fields.filter(is_customer_field=True, name=key).exists():
                self.fill_in_survey[key] = value
            if self.operation.tower_survey_fields.filter(is_customer_field=False, name=key).exists():
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

    @transition(field=state, source=RequestState.SUBMITTED, target=RequestState.NEED_INFO)
    def need_info(self):
        pass

    @transition(field=state, source=[RequestState.NEED_INFO, RequestState.REJECTED], target=RequestState.SUBMITTED)
    def re_submit(self):
        if self.approval_workflow_state is not None:
            self.approval_workflow_state.current_step.reset_to_pending()

    @transition(field=state, source=[RequestState.SUBMITTED,
                                     RequestState.NEED_INFO,
                                     RequestState.REJECTED,
                                     RequestState.ACCEPTED], target=RequestState.CANCELED)
    def cancel(self):
        # delete the related instance if the state was pending (we should have only one)
        if self.instance.state == InstanceState.PENDING:
            self.instance.delete()
            return False
        return True

    @transition(field=state, source=[RequestState.SUBMITTED, RequestState.ACCEPTED, RequestState.NEED_INFO],
                target=RequestState.REJECTED)
    def reject(self, user):
        pass

    @transition(field=state, source=[RequestState.ACCEPTED, RequestState.SUBMITTED, RequestState.FAILED],
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
            tower_job_id = self.operation.job_template.execute(extra_vars=tower_extra_vars,
                                                               inventory_override=inventory_override,
                                                               credentials_override=credentials_override,
                                                               tags_override=tags_override,
                                                               skip_tags_override=skip_tags_override,
                                                               limit_override=limit_override,
                                                               verbosity_override=verbosity_override,
                                                               job_type_override=job_type_override,
                                                               diff_mode_override=diff_mode_override)
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
                f"[Request][check_job_status] no tower job id for request id {self.id}. Check job status skipped")
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

        if job_object.status == "successful":
            logger.info(f"[Request][check_job_status] tower job status successful for request id {self.id}")
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
            error_message = f"Tower job {self.tower_job_id} status is '{job_object.status}'"
            self.has_failed(error_message)
            self.save()
            self.periodic_task.delete()
            send_mail_request_update(target_request=self)

    def setup_approval_workflow(self):
        from service_catalog.models import ApprovalWorkflow
        worfkflow = ApprovalWorkflow.objects.filter(operation=self.operation,
                                                    scopes__in=[self.instance.quota_scope]).first()
        if worfkflow:
            logger.debug(f"Workflow found: {worfkflow.name}")
            # create pending steps
            self.approval_workflow_state = worfkflow.instantiate()
            self.save()

    @classmethod
    def auto_accept_and_process_signal(cls, sender, instance, created, *args, **kwargs):
        """
        Switch state to accept or process automatically if target operation auto_accept or auto_process is true
        when creating the Request
        :param instance: the current Request
        :type instance: Request
        """
        if instance.operation.auto_accept:
            if instance.state == RequestState.SUBMITTED:
                if can_proceed(instance.accept):
                    instance.accept(None, save=False)
        if instance.operation.auto_process:
            if instance.state == RequestState.ACCEPTED:
                if can_proceed(instance.process):
                    instance.process(None, save=False)
                if can_proceed(instance.perform_processing):
                    instance.perform_processing()
                instance.save()

    @classmethod
    def trigger_hook_handler(cls, sender, instance, name, source, target, *args, **kwargs):
        """
        Proxy method. Cannot be mocked for testing
        """
        HookManager.trigger_hook(sender=sender, instance=instance, name=name, source=source, target=target,
                                 *args, **kwargs)

    @classmethod
    def on_create(cls, sender, instance, created, *args, **kwargs):
        if created:
            # notify hook manager
            HookManager.trigger_hook(sender=sender, instance=instance, name="create", source="create",
                                     target=RequestState.SUBMITTED, *args, **kwargs)

            # create approval step if approval workflow is set
            instance.setup_approval_workflow()

    @classmethod
    def on_change(cls, sender, instance, *args, **kwargs):
        # reset all approval step to pending if an approval workflow was attached to the request
        if instance.id is not None:
            previous = Request.objects.get(id=instance.id)
            if previous.state != RequestState.SUBMITTED and instance.state == RequestState.SUBMITTED:
                if instance.approval_workflow_state is not None:
                    instance.approval_workflow_state.reset()


pre_save.connect(Request.on_change, sender=Request)
post_save.connect(Request.auto_accept_and_process_signal, sender=Request)
post_transition.connect(Request.trigger_hook_handler, sender=Request)
post_save.connect(Request.on_create, sender=Request)
