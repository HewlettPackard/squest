from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to='service_image', blank=True)
