import copy
import json
import logging
from datetime import datetime, timedelta
import requests
import towerlib
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import JSONField, ForeignKey, CASCADE, SET_NULL, DateTimeField, IntegerField, TextField
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django_fsm import FSMField, transition, post_transition

from profiles.models import Team
from profiles.models.user_role_binding import UserRoleBinding
from profiles.models.team_role_binding import TeamRoleBinding
from profiles.models.role_manager import RoleManager
from service_catalog.models.approval_step import ApprovalStep
from service_catalog.models.approval_step_state import ApprovalStepState
from service_catalog.models.approval_state import ApprovalState
from service_catalog.models.operations import Operation, OperationType
from service_catalog.models.exceptions import ExceptionServiceCatalog
from service_catalog.models.request_state import RequestState
from service_catalog.models.instance import Instance, InstanceState
from service_catalog.models.state_hooks import HookManager

logger = logging.getLogger(__name__)


class Request(RoleManager):
    fill_in_survey = JSONField(default=dict, blank=True)
    admin_fill_in_survey = JSONField(default=dict, blank=True)
    instance = ForeignKey(Instance, on_delete=CASCADE, null=True)
    operation = ForeignKey(Operation, on_delete=CASCADE)
    user = ForeignKey(User, blank=True, null=True, on_delete=SET_NULL)
    date_submitted = DateTimeField(auto_now=True, blank=True, null=True)
    date_complete = DateTimeField(auto_now=False, blank=True, null=True)
    date_archived = DateTimeField(auto_now=False, blank=True, null=True)
    tower_job_id = IntegerField(blank=True, null=True)
    state = FSMField(default=RequestState.SUBMITTED, choices=RequestState.choices)
    periodic_task = ForeignKey(PeriodicTask, on_delete=SET_NULL, null=True, blank=True)
    periodic_task_date_expire = DateTimeField(auto_now=False, blank=True, null=True)
    failure_message = TextField(blank=True, null=True)
    approval_step = ForeignKey(
        ApprovalStep,
        blank=True,
        null=True,
        on_delete=SET_NULL,
        related_name='requests',
        related_query_name='request'
    )

    def __str__(self):
        return f"{self.operation.name} - {self.instance.name} (#{self.id})"

    @property
    def full_survey(self):
        return {k: v for k, v in {**self.fill_in_survey, **self.admin_fill_in_survey}.items() if v is not None}

    def clean(self):
        if self.fill_in_survey is None:
            raise ValidationError({'fill_in_survey': _("Please enter a valid JSON. Empty value is {} for JSON.")})

    def update_fill_in_surveys_accept_request(self, admin_provided_survey_fields):
        for key, value in admin_provided_survey_fields.items():
            if self.operation.tower_survey_fields.filter(enabled=True, name=key).exists():
                self.fill_in_survey[key] = value
            if self.operation.tower_survey_fields.filter(enabled=False, name=key).exists():
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
        return f"{self.operation.job_template.tower_server.url}/#/jobs"

    @transition(field=state, source=RequestState.SUBMITTED, target=RequestState.NEED_INFO)
    def need_info(self):
        pass

    @transition(field=state, source=RequestState.NEED_INFO, target=RequestState.SUBMITTED)
    def re_submit(self):
        pass

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
        self.state = self.get_state_from_approval_step(user, ApprovalState.REJECTED)
        self.save()

    @transition(field=state, source=[RequestState.ACCEPTED, RequestState.SUBMITTED, RequestState.FAILED],
                target=RequestState.ACCEPTED, permission='service_catalog.approve_request_approvalstep')
    def accept(self, user):
        self.state = self.get_state_from_approval_step(user, ApprovalState.APPROVED)
        self.save()

    @transition(field=state, source=[RequestState.ACCEPTED, RequestState.FAILED], target=RequestState.PROCESSING,
                conditions=[can_process])
    def process(self):
        logger.info(f"[Request][process] trying to start processing request '{self.id}'")
        # the instance now switch depending on the operation type
        if self.operation.type == OperationType.CREATE:
            self.instance.provisioning()
        elif self.operation.type == OperationType.UPDATE:
            self.instance.updating()
        elif self.operation.type == OperationType.DELETE:
            self.instance.deleting()
        self.instance.save()

    @transition(field=state, source=RequestState.PROCESSING)
    def perform_processing(self):
        # run Tower job
        tower_extra_vars = copy.copy(self.full_survey)
        # add the current instance to extra vars
        from service_catalog.api.serializers.request_serializers import AdminRequestSerializer
        from django.conf import settings
        tower_extra_vars["squest"] = {
            "squest_host": settings.SQUEST_HOST,
            "request": AdminRequestSerializer(self).data
        }
        tower_job_id = None
        try:
            tower_job_id = self.operation.job_template.execute(extra_vars=tower_extra_vars)
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

    def get_state_from_approval_step(self, user, target_approval_step_state):
        """
        This method return the calculated status from approval step states
        """
        if self.operation.approval_workflow is None and self.approval_step is None:
            if target_approval_step_state == ApprovalState.APPROVED:
                return RequestState.ACCEPTED
            elif target_approval_step_state == ApprovalState.REJECTED:
                return RequestState.REJECTED
            else:
                raise NotImplementedError
        bindings = UserRoleBinding.objects.filter(
            content_type=ContentType.objects.get(app_label="profiles", model="team"),
            user=user
        )
        teams = Team.objects.filter(id__in=[binding.object_id for binding in bindings])
        for approval_step_state in ApprovalStepState.objects.filter(team__in=teams, request=self,
                                                                    approval_step=self.approval_step):
            approval_step_state.set_state(user, target_approval_step_state)
        state = self.approval_step.get_request_approval_state(self)
        if state == ApprovalState.REJECTED:
            return RequestState.REJECTED
        elif state == ApprovalState.APPROVED:
            self.approval_step = self.approval_step.next
            if self.approval_step:
                from service_catalog.mail_utils import send_mail_request_update
                send_mail_request_update(
                    self,
                    plain_text=f"Request need your approval",
                    receiver_email_list=self.approval_step.get_approvers_emails()
                )
        if self.operation.approval_workflow and self.approval_step is None and self.state == RequestState.SUBMITTED:
            return RequestState.ACCEPTED
        return self.state

    @classmethod
    def set_default_approval_step(cls, sender, instance, *args, **kwargs):
        if not instance.id and instance.operation.approval_workflow:
            instance.approval_step = instance.operation.approval_workflow.entry_point

    @classmethod
    def create_approval_step_states_when_approval_step_changed(cls, sender, instance, *args, **kwargs):
        if instance.id:
            old = Request.objects.get(id=instance.id)
            if old.approval_step != instance.approval_step:
                if instance.approval_step:
                    for team in instance.approval_step.teams.all():
                        ApprovalStepState.objects.create(request=instance, approval_step=instance.approval_step,
                                                         team=team)

    @classmethod
    def create_approval_step_states(cls, sender, instance, created, *args, **kwargs):
        if created:
            if instance.approval_step:
                for team in instance.approval_step.teams.all():
                    ApprovalStepState.objects.create(request=instance, approval_step=instance.approval_step,
                                                     team=team)

    @classmethod
    def add_permission(cls, sender, instance, created, *args, **kwargs):
        if created:
            if instance.user:
                instance.add_user_in_role(instance.user, "Admin")
            instance_content_type = ContentType.objects.get_for_model(Instance)
            user_bindings = UserRoleBinding.objects.filter(
                content_type=instance_content_type,
                object_id=instance.instance.id
            )
            team_bindings = TeamRoleBinding.objects.filter(
                content_type=instance_content_type,
                object_id=instance.instance.id
            )
            for user_binding in user_bindings:
                instance.add_user_in_role(user_binding.user, user_binding.role.name)
            for team_binding in team_bindings:
                instance.add_team_in_role(team_binding.team, team_binding.role.name)

    @classmethod
    def accept_if_auto_accept_on_operation(cls, sender, instance, created, *args, **kwargs):
        """
        Switch state to accept automatically if target operation auto_accept is true
        when creating the Request
        :param instance: the current Request
        :type instance: Request
        """
        if created:
            if instance.operation.auto_accept:
                instance.accept(None)
                instance.save()

    @classmethod
    def process_if_auto_auto_process_on_operation(cls, sender, instance, created, *args, **kwargs):
        """
        Switch state to processing automatically if target operation auto_process is true
        when creating the Request
        :param instance: the current Request
        :type instance: Request
        """
        if created:
            if instance.state == RequestState.ACCEPTED:
                if instance.operation.auto_process:
                    instance.process()
                    instance.save()
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
    def on_create_call_hook_manager(cls, sender, instance, created, *args, **kwargs):
        if created:
            HookManager.trigger_hook(sender=sender, instance=instance, name="create", source="create",
                                     target=RequestState.SUBMITTED, *args, **kwargs)


@receiver(pre_delete, sender=Instance)
def pre_delete(sender, instance, **kwargs):
    instance.remove_all_bindings()


pre_save.connect(Request.set_default_approval_step, sender=Request)
pre_save.connect(Request.create_approval_step_states_when_approval_step_changed, sender=Request)
post_save.connect(Request.create_approval_step_states, sender=Request)
post_save.connect(Request.add_permission, sender=Request)
post_save.connect(Request.accept_if_auto_accept_on_operation, sender=Request)
post_save.connect(Request.process_if_auto_auto_process_on_operation, sender=Request)
post_transition.connect(Request.trigger_hook_handler, sender=Request)
post_save.connect(Request.on_create_call_hook_manager, sender=Request)
