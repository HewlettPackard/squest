from django.db import models
from django_fsm import FSMField, transition

from . import Operation
from .instance import Instance


class Request(models.Model):
    fill_in_survey = models.JSONField(default=dict)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
    state = FSMField(default='SUBMITTED')

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
        # TODO: celery task call tower
        pass

    @transition(field=state, source='PROCESSING', target='FAILED')
    def has_failed(self):
        pass

    @transition(field=state, source='PROCESSING', target='COMPLETE')
    def complete(self):
        pass
