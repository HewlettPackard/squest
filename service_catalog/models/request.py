from django.db import models
from jsonfield import JSONField

from . import Operation
from .instance import Instance


class Request(models.Model):
    fill_in_survey = JSONField()
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
