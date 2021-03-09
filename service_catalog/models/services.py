from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    # TODO image
