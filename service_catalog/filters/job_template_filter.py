from service_catalog.models import JobTemplate
from Squest.utils.squest_filter import SquestFilter


class JobTemplateFilter(SquestFilter):
    class Meta:
        model = JobTemplate
        fields = ['name', 'is_compliant']
