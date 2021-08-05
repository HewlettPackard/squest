from django.db import models
from django.contrib import admin

from martor.widgets import AdminMartorWidget

from service_catalog.models.documentation import Doc


class DocAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }


admin.site.register(Doc, DocAdmin)
