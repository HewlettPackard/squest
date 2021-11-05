from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from service_catalog.models import Service


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    notification_enabled = models.BooleanField(default=True)
    subscribed_services_notification = models.ManyToManyField(Service)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
