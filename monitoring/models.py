from django.contrib.auth.models import User
from django.db.models import Count
from prometheus_client import Summary
from prometheus_client.metrics_core import GaugeMetricFamily

from service_catalog.models import Instance, Support, Request


# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')


class ComponentCollector(object):

    @REQUEST_TIME.time()
    def collect(self):
        yield self.get_total_squest_instance_per_service_name()
        yield self.get_total_squest_instance_per_state()
        yield self.get_total_squest_request_per_state()
        yield self.get_total_instance()
        yield self.get_total_request()
        yield self.get_total_support()
        yield self.get_total_users()
        yield self.get_total_teams()

    @staticmethod
    def get_total_squest_instance_per_service_name():
        field_name = 'service__name'
        instances = Instance.objects.values(field_name).order_by(field_name).annotate(counter=Count(field_name))
        gauge_squest_instance_total = GaugeMetricFamily("squest_instance_per_service_total",
                                                        'Total number of instance per service in squest',
                                                        labels=['service'])
        for instance in instances:
            gauge_squest_instance_total.add_metric([instance["service__name"]], instance["counter"])
        return gauge_squest_instance_total

    @staticmethod
    def get_total_squest_instance_per_state():
        field_name = 'state'
        instances = Instance.objects.values(field_name).order_by(field_name).annotate(counter=Count(field_name))
        gauge_squest_instance_total = GaugeMetricFamily("squest_instance_per_state_total",
                                                        'Total number of instance per state in squest',
                                                        labels=['state'])
        for instance in instances:
            gauge_squest_instance_total.add_metric([instance["state"]], instance["counter"])
        return gauge_squest_instance_total

    @staticmethod
    def get_total_squest_request_per_state():
        field_name = 'state'
        requests = Request.objects.values(field_name).order_by(field_name).annotate(counter=Count(field_name))
        gauge = GaugeMetricFamily("squest_request_per_state_total",
                                  'Total number of request per state in squest',
                                  labels=['state'])
        for request in requests:
            gauge.add_metric([request["state"]], request["counter"])
        return gauge

    @staticmethod
    def get_total_instance():
        """
        Get all instances
        Labels: service__name, instance_state, scope_name
        squest_instance_total{state="AVAILABLE", service="K8S", scope="5G"} 1.0
        squest_instance_total{state="PENDING", service="K8S", scope="5G"} 2.0
        """
        gauge_squest_instance_total = GaugeMetricFamily("squest_instance_total",
                                                        'Total number of instance in squest',
                                                        labels=['service', 'state', 'scope'])
        instances = Instance.objects.values('service__name',
                                            'scope__name',
                                            'state').annotate(total_count=Count('id'))
        for instance in instances:
            if instance["scope__name"] is not None:
                scope_name = instance["scope__name"]
            else:
                scope_name = "None"
            gauge_squest_instance_total.add_metric([instance["service__name"],
                                                    instance["state"],
                                                    scope_name],
                                                   instance["total_count"])
        return gauge_squest_instance_total

    @staticmethod
    def get_total_support():
        gauge = GaugeMetricFamily("squest_support_total",
                                  'Total number of support in squest',
                                  labels=['service', 'state'])
        supports = Support.objects.values('instance__service__name',
                                          'state').annotate(total_count=Count('id'))
        for support in supports:
            gauge.add_metric([support["instance__service__name"],
                              support["state"]],
                             support["total_count"])
        return gauge

    @staticmethod
    def get_total_users():
        gauge = GaugeMetricFamily("squest_user_total",
                                  'Total number of user in squest',
                                  labels=['is_superuser'])
        gauge.add_metric(["true"], User.objects.filter(is_superuser=True).count())
        gauge.add_metric(["false"], User.objects.filter(is_superuser=False).count())
        return gauge

    @staticmethod
    def get_total_teams():
        gauge = GaugeMetricFamily("squest_team_total",
                                  'Total number of team in squest')
        gauge.add_metric([], 1)
        return gauge

    @staticmethod
    def get_total_request():
        gauge = GaugeMetricFamily("squest_request_total",
                                  'Total number of request in squest',
                                  labels=['service', 'state'])
        requests = Request.objects.values('instance__service__name',
                                          'state').annotate(total_count=Count('id'))
        for request in requests:
            gauge.add_metric([request["instance__service__name"],
                              request["state"]],
                             request["total_count"])
        return gauge
