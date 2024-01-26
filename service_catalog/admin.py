from django.contrib import admin
from django.db import models
from martor.widgets import AdminMartorWidget

from service_catalog.models.documentation import Doc


class DocAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }

    list_filter = ['services', 'operations']
    list_display = ['title', 'linked_services', 'linked_operations']

    def linked_services(self, obj):
        return ", ".join([str(service) for service in obj.services.all()])

    def linked_operations(self, obj):
        return ", ".join([str(operation) for operation in obj.operations.all()])


admin.site.register(Doc, DocAdmin)
