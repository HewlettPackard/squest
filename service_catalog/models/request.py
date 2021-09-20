import copy
import json
import logging
from datetime import datetime, timedelta

import requests
import towerlib
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django_fsm import FSMField, transition, post_transition
from guardian.models import UserObjectPermission

from . import Operation, ExceptionServiceCatalog, InstanceState, OperationType
from .instance import Instance
from .state_hooks import HookManager

logger = logging.getLogger(__name__)


class RequestState(models.TextChoices):
    SUBMITTED = 'SUBMITTED', _('SUBMITTED')
    NEED_INFO = 'NEED_INFO', _('NEED_INFO')
    REJECTED = 'REJECTED', _('REJECTED')
    ACCEPTED = 'ACCEPTED', _('ACCEPTED')
    CANCELED = 'CANCELED', _('CANCELED')
    PROCESSING = 'PROCESSING', _('PROCESSING')
    COMPLETE = 'COMPLETE', _('COMPLETE')
    FAILED = 'FAILED', _('FAILED')


class Request(models.Model):
    fill_in_survey = models.JSONField(default=dict)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    date_submitted = models.DateTimeField(auto_now=True, blank=True, null=True)
    date_complete = models.DateTimeField(auto_now=False, blank=True, null=True)
    tower_job_id = models.IntegerField(blank=True, null=True)
    state = FSMField(default=RequestState.SUBMITTED, choices=RequestState.choices)
    periodic_task = models.ForeignKey(PeriodicTask, on_delete=models.SET_NULL, null=True, blank=True)
    periodic_task_date_expire = models.DateTimeField(auto_now=False, blank=True, null=True)
    failure_message = models.TextField(blank=True, null=True)

    def instance_is_available_or_pending(self):
        if self.instance.state == InstanceState.AVAILABLE or self.instance.state == InstanceState.PENDING:
            return True
        logger.debug(f"Request][process] instance {self.id} is not available or pending")
        return False

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
        instance = Instance.objects.get(request=self)
        if instance.state == InstanceState.PENDING:
            instance.delete()

    @transition(field=state, source=[RequestState.SUBMITTED, RequestState.ACCEPTED, RequestState.NEED_INFO],
                target=RequestState.REJECTED)
    def reject(self):
        pass

    @transition(field=state, source=[RequestState.SUBMITTED, RequestState.FAILED], target=RequestState.ACCEPTED)
    def accept(self):
        pass

    @transition(field=state, source=RequestState.ACCEPTED, target=RequestState.PROCESSING,
                conditions=[instance_is_available_or_pending])
    def process(self):
        logger.info(f"[Request][process] trying to start processing request '{self.id}'")
        # the instance now switch depending of the operation type
        if self.operation.type == OperationType.CREATE:
            self.instance.provisioning()
        if self.operation.type == OperationType.UPDATE:
            self.instance.updating()
        if self.operation.type == OperationType.DELETE:
            self.instance.deleting()
        self.instance.save()

    @transition(field=state, source=RequestState.PROCESSING)
    def perform_processing(self):
        # run Tower job
        tower_extra_vars = copy.copy(self.fill_in_survey)
        # add the current instance to extra vars
        from ..serializers.request_serializer import RequestSerializer
        tower_extra_vars["squest"] = {
            "request": RequestSerializer(self).data
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

        if tower_job_id is not None:
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
                f'[Request][process] request \'{self.id}\': periodic task created. Expire in {self.operation.process_timeout_second} seconds')

    @transition(field=state, source=RequestState.PROCESSING, target=RequestState.FAILED)
    def has_failed(self, reason=None):
        if reason is not None:
            self.failure_message = reason
        if self.operation.type == OperationType.CREATE:
            self.instance.provisioning_has_failed()
        if self.operation.type == OperationType.UPDATE:
            self.instance.update_has_failed()
        if self.operation.type == OperationType.DELETE:
            self.instance.delete_has_failed()
        self.instance.save()

    @transition(field=state, source=RequestState.PROCESSING, target=RequestState.COMPLETE)
    def complete(self):
        self.date_complete = datetime.now()

    def delete(self, *args, **kwargs):
        if self.periodic_task is not None:
            self.periodic_task.delete()
        return super(self.__class__, self).delete(*args, **kwargs)

    def check_job_status(self):
        from ..mail_utils import send_mail_request_update, send_email_request_error
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
                self.instance.available()
                self.instance.save()
            if self.operation.type == OperationType.DELETE:
                self.instance.deleted()
                self.instance.save()
            # notify owner and admins that the request is complete
            send_mail_request_update(target_request=self)

        if job_object.status == "canceled":
            error_message = f"Tower job '{self.tower_job_id}' status is 'canceled'"
            self.has_failed(error_message)
            self.save()
            # as the process has been cancelled, set back the instance to available
            self.instance.available()
            self.instance.save()
            self.periodic_task.delete()
            send_email_request_error(target_request=self,
                                     error_message=error_message)

        if job_object.status == "failed":
            error_message = f"Tower job '{self.tower_job_id}' status is 'failed'"
            self.has_failed(error_message)
            self.save()
            self.periodic_task.delete()
            send_email_request_error(target_request=self,
                                     error_message=error_message)

    @classmethod
    def add_user_permission(cls, sender, instance, created, *args, **kwargs):
        if created:
            if instance.user is not None:
                logger.info(
                    f"[Request][add_user_permission] add user permission on request id {instance.id} for user {instance.user.username}")
                UserObjectPermission.objects.assign_perm('view_request', instance.user, obj=instance)
                UserObjectPermission.objects.assign_perm('delete_request', instance.user, obj=instance)

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
                instance.accept()
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


post_save.connect(Request.add_user_permission, sender=Request)
post_save.connect(Request.accept_if_auto_accept_on_operation, sender=Request)
post_save.connect(Request.process_if_auto_auto_process_on_operation, sender=Request)
post_transition.connect(HookManager.trigger_hook_handler, sender=Request)
