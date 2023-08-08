from rest_framework.generics import get_object_or_404

from Squest.utils.squest_api_views import SquestRetrieveUpdateAPIView, SquestListAPIView
from service_catalog.api.serializers import JobTemplateSerializer
from service_catalog.filters.job_template_filter import JobTemplateFilter
from service_catalog.models import JobTemplate, AnsibleController


class JobTemplateDetails(SquestRetrieveUpdateAPIView):
    serializer_class = JobTemplateSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return JobTemplate.objects.none()
        ansible_controller = get_object_or_404(AnsibleController, id=self.kwargs.get('ansible_controller_id'))
        job_template_id = self.kwargs.get('pk')
        return JobTemplate.objects.filter(id=job_template_id, ansible_controller__id=ansible_controller.id)


class JobTemplateList(SquestListAPIView):
    serializer_class = JobTemplateSerializer
    filterset_class = JobTemplateFilter

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return JobTemplate.objects.none()
        ansible_controller = get_object_or_404(AnsibleController, id=self.kwargs.get('ansible_controller_id'))
        return JobTemplate.objects.filter(ansible_controller__id=ansible_controller.id)
