from django.db import models

from .tower_server import TowerServer
from django.db.models.signals import post_save
from django.dispatch import receiver


class JobTemplate(models.Model):
    name = models.CharField(max_length=100)
    tower_id = models.IntegerField()
    survey = models.JSONField(default=dict)
    tower_server = models.ForeignKey(TowerServer, on_delete=models.CASCADE)
    ask_variables_on_launch = models.BooleanField(default=False,
                                                  help_text="Please enable ask_variables_on_launch on your job_templates")

    class Meta:
        unique_together = ('tower_id', 'tower_server',)

    def __str__(self):
        return f"{self.name} ({self.tower_server.name})"

    def execute(self, extra_vars):
        tower_job_template = self.get_tower_job_template()
        tower_job_run = tower_job_template.launch(extra_vars=extra_vars)
        return tower_job_run.id

    def get_tower_job_template(self):
        return self.tower_server.get_tower_instance().get_job_template_by_id(self.tower_id)

    def set_ask_variables_on_launch(self, value: bool):
        self.get_tower_job_template()._update_values("ask_variables_on_launch", value)


@receiver(post_save, sender=JobTemplate)
def ask_variables_on_launch(sender, instance: JobTemplate, **kwargs):
    instance.set_ask_variables_on_launch(instance.ask_variables_on_launch)

