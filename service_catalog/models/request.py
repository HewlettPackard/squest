import json
import logging

from django.db import models
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django_fsm import FSMField, transition

from . import Operation
from .instance import Instance

logger = logging.getLogger(__name__)


class Request(models.Model):
    fill_in_survey = models.JSONField(default=dict)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
    tower_job_id = models.IntegerField(blank=True, null=True)
    state = FSMField(default='SUBMITTED')
    periodic_task = models.ForeignKey(PeriodicTask, on_delete=models.SET_NULL, null=True, blank=True)

    @transition(field=state, source='SUBMITTED', target='NEED_INFO')
    def need_info(self):
        pass

    @transition(field=state, source='NEED_INFO', target='SUBMITTED')
    def re_submit(self):
        pass

    @transition(field=state, source=['SUBMITTED', 'NEED_INFO', 'REJECTED', 'ACCEPTED'], target='CANCELED')
    def cancel(self):
        # delete the related instance (we should have only one)
        instance = Instance.objects.get(request=self)
        instance.delete()

    @transition(field=state, source=['SUBMITTED', 'ACCEPTED', 'NEED_INFO'], target='REJECTED')
    def reject(self):
        pass

    @transition(field=state, source='SUBMITTED', target='ACCEPTED')
    def accept(self):
        pass

    @transition(field=state, source='ACCEPTED', target='PROCESSING')
    def process(self):
        logger.info("[Request][process] trying to start processing request '{}'".format(self.id))
        # run Tower job
        tower_job_id = self.operation.job_template.execute(extra_vars=self.fill_in_survey)
        self.tower_job_id = tower_job_id
        logger.info("[Request][process] process started on request '{}'. "
                    "Tower job id: {}".format(self.id, tower_job_id))
        # the instance now switch depending of the operation type
        if self.operation.type == "CREATE":
            self.instance.provisioning()
        if self.operation.type == "UPDATE":
            self.instance.update()
        if self.operation.type == "DELETE":
            self.instance.deleting()
        self.instance.save()
        # create a periodic task to check the status until job is complete
        schedule, created = IntervalSchedule.objects.get_or_create(every=10,
                                                                   period=IntervalSchedule.SECONDS)
        self.periodic_task = PeriodicTask.objects.create(
            interval=schedule,
            name='job_status_check_request_{}'.format(self.id),
            task='service_catalog.tasks.check_tower_job_status_task',
            args=json.dumps([self.id]))
        self.save()

    @transition(field=state, source='PROCESSING', target='FAILED')
    def has_failed(self):
        pass

    @transition(field=state, source='PROCESSING', target='COMPLETE')
    def complete(self):
        pass

    def delete(self, *args, **kwargs):
        if self.periodic_task is not None:
            self.periodic_task.delete()
        return super(self.__class__, self).delete(*args, **kwargs)

    def check_job_status(self):
        if self.tower_job_id is None:
            logger.warning("[Request][check_job_status] no tower job id for request id {}. "
                           "Check job status skipped".format(self.id))
            return

        tower = self.operation.job_template.tower_server.get_tower_instance()
        job_object = tower.get_unified_job_by_id(self.tower_job_id)

        if job_object.status == "successful":
            logger.info("[Request][check_job_status] tower job status successful for request id {}".format(self.id))
            self.complete()
            self.save()
            self.periodic_task.delete()
            if self.operation.type in ["CREATE", "UPDATE"]:
                self.instance.available()
                self.instance.save()
            if self.operation.type == "DELETE":
                self.instance.deleted()
                self.instance.save()

        if job_object.status == "canceled":
            self.has_failed()
            self.save()
            self.instance.available()
            self.instance.save()
            self.periodic_task.delete()

        if job_object.status == "failed":
            self.has_failed()
            self.save()
            self.periodic_task.delete()
            if self.operation.type == "CREATE":
                self.instance.provisioning_has_failed()
            if self.operation.type == "UPDATE":
                self.instance.update_has_failed()
            if self.operation.type == "DELETE":
                self.instance.delete_has_failed()
