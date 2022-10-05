from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    notification_enabled = models.BooleanField(default=True)

    def is_notification_authorized(self, request=None):
        if self.notification_filters.count() == 0 or request is None:
            return True
        is_notification_authorized = False
        for notification_filter in self.notification_filters.all():
            if notification_filter.is_authorized(request):
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
