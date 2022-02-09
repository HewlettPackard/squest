from django.db.models.signals import post_save, post_delete


def skip_auto_calculation(func):
    def _skip_auto_calculation(self, *args, **kwargs):
        from resource_tracker.models import ResourceAttribute
        from resource_tracker.models import Resource
        from resource_tracker.models.resource_attribute import on_change
        from resource_tracker.models.resource import on_delete
        post_save.disconnect(on_change, sender=ResourceAttribute)
        post_delete.disconnect(on_delete, sender=Resource)
        response = func(self, *args, **kwargs)
        post_save.connect(on_change, sender=ResourceAttribute)
        post_delete.connect(on_delete, sender=Resource)
        return response

    return _skip_auto_calculation
