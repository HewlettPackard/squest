import sys

from django.apps import AppConfig
import prometheus_client


class MonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitoring'

    def ready(self):
        if 'manage.py' not in sys.argv:
            from .models import ComponentCollector
            prometheus_client.REGISTRY.register(ComponentCollector())
            # Unregister default metrics
            prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)
            prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
            # Unlike process and platform_collector gc_collector registers itself
            prometheus_client.REGISTRY.unregister(prometheus_client.REGISTRY._names_to_collectors['python_gc_collections_total'])
