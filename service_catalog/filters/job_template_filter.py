from Squest.utils.squest_filter import SquestFilter
from service_catalog.models import JobTemplate


class JobTemplateFilter(SquestFilter):
    class Meta:
        model = JobTemplate
        fields = ['tower_server', 'name', 'is_compliant']
