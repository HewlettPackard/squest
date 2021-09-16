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

    def sync(self, job_template_id=None):
        """
        Sync all job templates
        :return:
        """
        from .job_templates import JobTemplate as JobTemplateLocal
        tower = self.get_tower_instance()
        if job_template_id is None:
            id_in_tower = []
            for job_template_from_tower in tower.job_templates:
                id_in_tower.append(job_template_from_tower.id)
                self._update_job_template_from_tower(job_template_from_tower)
            JobTemplateLocal.objects.all().exclude(tower_id__in=id_in_tower).delete()
        else:
            job_template = JobTemplateLocal.objects.get(id=job_template_id)
            self._update_job_template_from_tower(tower.get_job_template_by_id(job_template.tower_id))

    def get_tower_instance(self):
        return Tower(self.host, None, None, secure=self.secure, ssl_verify=self.ssl_verify, token=self.token)

    def _update_job_template_from_tower(self, job_template_from_tower):
        from .job_templates import JobTemplate as JobTemplateLocal
        job_template, _ = JobTemplateLocal.objects.get_or_create(tower_id=job_template_from_tower.id,
                                                                 tower_server=self,
                                                                 defaults={'name': job_template_from_tower.name})
        # update data
        job_template.name = job_template_from_tower.name
        job_template.tower_job_template_data = job_template_from_tower._data
        job_template.survey = job_template_from_tower.survey_spec
        job_template.is_compliant = job_template.check_is_compliant()
        job_template.save()
        # update all operation that uses this template
        from service_catalog.models import Operation
        Operation.update_survey_after_job_template_update(job_template)
