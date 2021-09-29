from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from . import BootstrapType, ExceptionServiceCatalog, TowerServer


class JobTemplate(models.Model):
    name = models.CharField(max_length=100)
    tower_id = models.IntegerField()
    survey = models.JSONField(default=dict)
    tower_server = models.ForeignKey(TowerServer, on_delete=models.CASCADE)
    tower_job_template_data = models.JSONField(default=dict)
    is_compliant = models.BooleanField(default=False)

    @property
    def tower_url(self):
        protocol = "https" if self.tower_server.secure else "http"
        return f"{protocol}://{self.tower_server.host}/#/templates/job_template/{self.tower_id}"

    class Meta:
        unique_together = ('tower_id', 'tower_server',)

    def __str__(self):
        return f"{self.name} ({self.tower_server.name})"

    def execute(self, extra_vars):
        tower_job_template = self.tower_server.get_tower_instance().get_job_template_by_id(self.tower_id)
        if tower_job_template is None:
            raise ExceptionServiceCatalog.JobTemplateNotFound(tower_name=self.tower_server.name,
                                                              job_template_id=self.tower_id)
        tower_job_run = tower_job_template.launch(extra_vars=extra_vars)
        return tower_job_run.id

    def check_is_compliant(self):
        return self.is_ask_variables_on_launch_compliant()

    def get_compliancy_details(self):
        return [
            dict(
                name='Variables/Prompt on launch',
                description='By default, recent version of AWX/Tower drop extra variables that are not declared in the '
                            'survey. To be able to receive Squest extra vars you need to enable "Prompt on Launch" in '
                            'the "Variables" section of you job template. This correspond to the flag '
                            '"ask_variables_on_launch" of the job_template model on the Tower/AWX API.',
                state=self.is_ask_variables_on_launch_compliant(),
                type=BootstrapType.SUCCESS if self.is_ask_variables_on_launch_compliant() else BootstrapType.WARNING,
            )
        ]

    # Compliance checks
    def is_ask_variables_on_launch_compliant(self):
        return self.tower_job_template_data['ask_variables_on_launch']


@receiver(pre_delete, sender=JobTemplate)
def job_template_delete(sender, instance, using, **kwargs):
    from . import Service, OperationType
    Service.objects.filter(operation__job_template=instance, operation__type__exact=OperationType.CREATE).update(
        **{"enabled": False})
