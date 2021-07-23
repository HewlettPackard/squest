from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to='service_image', blank=True)
    billing_group_id = models.IntegerField(null=True)
    billing_group_is_displayed = models.BooleanField(default=False)
    is_restricted_billing_groups = models.BooleanField(default=True)
