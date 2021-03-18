from django.db import models

from .tower_server import TowerServer


class JobTemplate(models.Model):
    name = models.CharField(max_length=100)
    tower_id = models.IntegerField()
    survey = models.JSONField(default=dict)
    tower_server = models.ForeignKey(TowerServer, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
