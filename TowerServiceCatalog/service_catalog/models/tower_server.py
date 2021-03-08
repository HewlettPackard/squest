from django.db import models
from towerlib import Tower

from .job_templates import JobTemplate as JobTemplateLocal


class TowerServer(models.Model):
    name = models.CharField(max_length=100)
    host = models.CharField(max_length=200, unique=True)
    token = models.CharField(max_length=200)
    secure = models.BooleanField(default=True)
    ssl_verify = models.BooleanField(default=False)

    def sync(self):
        """
        Sync all job templates
        :return:
        """
        tower = Tower(self.host, None, None, secure=self.secure, ssl_verify=self.ssl_verify, token=self.token)
        test_survey = {
            "key": "value"
        }
        for job_template in tower.job_templates:
            try:
                JobTemplateLocal.objects.get(tower_id=job_template.id)
            except JobTemplateLocal.DoesNotExist:
                JobTemplateLocal.objects.create(name=job_template.name, tower_id=job_template.id, survey=test_survey)
