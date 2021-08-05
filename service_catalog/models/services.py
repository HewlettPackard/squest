from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to='service_image', blank=True)
    billing_group_id = models.IntegerField(null=True, default=None)
    billing_group_is_shown = models.BooleanField(default=False)
    billing_group_is_selectable = models.BooleanField(default=False)
    billing_groups_are_restricted = models.BooleanField(default=True)

    def __str__(self):
        return self.name
