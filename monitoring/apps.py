import sys

from django.apps import AppConfig
import prometheus_client

class MonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitoring'

    def ready(self):
        if 'manage.py' not in sys.argv and 'test' not in sys.argv:
            from .models import ComponentCollector
            prometheus_client.REGISTRY.register(ComponentCollector())
