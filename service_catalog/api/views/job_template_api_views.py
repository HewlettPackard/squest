from rest_framework.generics import get_object_or_404

from Squest.utils.squest_api_views import SquestRetrieveUpdateAPIView, SquestListAPIView
from service_catalog.filters.job_template_filter import JobTemplateFilter
from service_catalog.models import JobTemplate, TowerServer
from service_catalog.api.serializers import JobTemplateSerializer


class JobTemplateDetails(SquestRetrieveUpdateAPIView):
    serializer_class = JobTemplateSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return JobTemplate.objects.none()
        tower_server = get_object_or_404(TowerServer, id=self.kwargs.get('tower_server_id'))
        job_template_id = self.kwargs.get('pk')
        return JobTemplate.objects.filter(id=job_template_id, tower_server__id=tower_server.id)


class JobTemplateList(SquestListAPIView):
    serializer_class = JobTemplateSerializer
    filterset_class = JobTemplateFilter

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return JobTemplate.objects.none()
        tower_server = get_object_or_404(TowerServer, id=self.kwargs.get('tower_server_id'))
        return JobTemplate.objects.filter(tower_server__id=tower_server.id)
