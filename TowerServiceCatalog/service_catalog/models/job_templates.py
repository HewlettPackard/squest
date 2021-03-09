from django.db import models
from jsonfield import JSONField

from .tower_server import TowerServer


class JobTemplate(models.Model):
    name = models.CharField(max_length=100)
    tower_id = models.IntegerField()
    survey = JSONField()
    tower_server = models.ForeignKey(TowerServer, on_delete=models.CASCADE)
