from django.db import models

from .tower_server import TowerServer


class JobTemplate(models.Model):
    name = models.CharField(max_length=100)
    tower_id = models.IntegerField()
    survey = models.JSONField(default=dict)
    tower_server = models.ForeignKey(TowerServer, on_delete=models.CASCADE)

    def __str__(self):
        return "{} ({})".format(self.name, self.tower_server.name)

    def execute(self, extra_vars):
        tower = self.tower_server.get_tower_instance()
        tower_job_template = tower.get_job_template_by_id(self.tower_id)
        tower_job_run = tower_job_template.launch(extra_vars=extra_vars)
        return tower_job_run.id
