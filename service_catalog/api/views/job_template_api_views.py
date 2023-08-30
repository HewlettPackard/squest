from Squest.utils.squest_api_views import SquestListAPIView, SquestRetrieveAPIView
from service_catalog.api.serializers import JobTemplateSerializer
from service_catalog.filters.job_template_filter import JobTemplateFilter
from service_catalog.models import JobTemplate


class JobTemplateDetails(SquestRetrieveAPIView):
    serializer_class = JobTemplateSerializer
    queryset = JobTemplate.objects.all()


class JobTemplateList(SquestListAPIView):
    serializer_class = JobTemplateSerializer
    filterset_class = JobTemplateFilter
    queryset = JobTemplate.objects.all()
