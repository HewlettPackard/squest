from django.db import models

from . import BootstrapType
from .tower_server import TowerServer


class JobTemplate(models.Model):
    name = models.CharField(max_length=100)
    tower_id = models.IntegerField()
    survey = models.JSONField(default=dict)
    tower_server = models.ForeignKey(TowerServer, on_delete=models.CASCADE)
    tower_job_template_data = models.JSONField(default=dict)
    compliant = models.BooleanField(default=False)

    class Meta:
        unique_together = ('tower_id', 'tower_server',)

    def __str__(self):
        return f"{self.name} ({self.tower_server.name})"

    def execute(self, extra_vars):
        tower_job_template = self.tower_server.get_tower_instance().get_job_template_by_id(self.tower_id)
        tower_job_run = tower_job_template.launch(extra_vars=extra_vars)
        return tower_job_run.id

    def is_compliant(self):
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

    ## Compliancy checks

    def is_ask_variables_on_launch_compliant(self):
        return self.tower_job_template_data['ask_variables_on_launch']
