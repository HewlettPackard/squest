from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    request_notification_enabled = models.BooleanField(default=True)
    instance_notification_enabled = models.BooleanField(default=True)
    theme = models.CharField(default="dark", max_length=20)

    def is_notification_authorized_for_request(self, request):
        from profiles.models import RequestNotification
        if RequestNotification.objects.filter(profile=self).count() == 0:
            return True
        is_notification_authorized = False
        for request_notification_filter in RequestNotification.objects.filter(profile=self):
            if request_notification_filter.is_authorized(request):
                is_notification_authorized = True
                break
        return is_notification_authorized

    def is_notification_authorized_for_instance(self, instance):
        from profiles.models.instance_notification import InstanceNotification
        if InstanceNotification.objects.filter(profile=self).count() == 0:
            return True
        is_notification_authorized = False
        for instance_notification_filter in InstanceNotification.objects.filter(profile=self):
            if instance_notification_filter.is_authorized(instance):
                is_notification_authorized = True
                break
        return is_notification_authorized


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
