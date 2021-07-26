from django.db import models

from service_catalog.models import Service, JobTemplate


class ServiceStateHook(models.Model):
    instance = models.ForeignKey(Service,
                                 on_delete=models.CASCADE,
                                 related_name='instances',
                                 related_query_name='instance',
                                 null=True)
    model = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    job_template = models.ForeignKey(JobTemplate, on_delete=models.CASCADE)


class GlobalHook(models.Model):
    name = models.CharField(unique=True, max_length=100)
    model = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    job_template = models.ForeignKey(JobTemplate, on_delete=models.CASCADE)
