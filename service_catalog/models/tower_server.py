from django.db import models
from towerlib import Tower


class TowerServer(models.Model):
    name = models.CharField(max_length=100)
    host = models.CharField(max_length=200, unique=True)
    token = models.CharField(max_length=200)
    secure = models.BooleanField(default=True)
    ssl_verify = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.host})"

    def sync(self):
        """
        Sync all job templates
        :return:
        """
        from .job_templates import JobTemplate as JobTemplateLocal
        tower = self.get_tower_instance()

        for job_template_from_tower in tower.job_templates:
            job_template, _ = JobTemplateLocal.objects.get_or_create(tower_id=job_template_from_tower.id,
                                                                     tower_server=self,
                                                                     defaults={'name': job_template_from_tower.name})
            # update the survey
            job_template.ask_variables_on_launch = job_template_from_tower.ask_variables_on_launch
            job_template.survey = job_template_from_tower.survey_spec
            job_template.save()
            # update all operation that uses this template
            from service_catalog.models import Operation
            Operation.update_survey_after_job_template_update(job_template)

    def get_tower_instance(self):
        return Tower(self.host, None, None, secure=self.secure, ssl_verify=self.ssl_verify, token=self.token)
