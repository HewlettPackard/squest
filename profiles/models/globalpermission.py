from django.contrib.auth.models import User
from django.urls import reverse
from profiles.models import AbstractScope


class GlobalPermission(AbstractScope):

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("profiles:globalpermission_details")

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = GlobalPermission.objects.get_or_create(name="GlobalPermission")
        return obj

    def get_potential_users(self):
        return User.objects.all()

    def get_scopes(self):
        return AbstractScope.objects.filter(id=self.id)
