from django.db.models import BooleanField
from django.contrib import admin


from Squest.models.singleton_model import SingletonModel


class SquestSettings(SingletonModel):
    maintenance_mode_enabled = BooleanField(default=False)


admin.site.register(SquestSettings)
