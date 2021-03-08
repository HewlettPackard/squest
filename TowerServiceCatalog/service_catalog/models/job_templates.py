from django.db import models
from jsonfield import JSONField


class JobTemplate(models.Model):
    name = models.CharField(max_length=100)
    tower_id = models.IntegerField()
    survey = JSONField()
