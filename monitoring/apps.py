import sys

from django.apps import AppConfig
import prometheus_client
from django.db.models.signals import post_migrate


def run_prometheus_metrics(sender, **kwargs):
    from .models import ComponentCollector
    prometheus_client.REGISTRY.register(ComponentCollector())


class MonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitoring'

    def ready(self):
        banned_words = ['test']
        if not any(banned_word in sys.argv for banned_word in banned_words):
            post_migrate.connect(run_prometheus_metrics, sender=self)
