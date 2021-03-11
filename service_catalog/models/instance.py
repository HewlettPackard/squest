from django.contrib.auth.models import User, Permission
from django.db import models
from jsonfield import JSONField

from . import Service


class Instance(models.Model):
    name = models.CharField(max_length=100)
    spec = JSONField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)


class UserPermissionOnInstance(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_permission_on_instance'
        unique_together = ('instance', 'user')
