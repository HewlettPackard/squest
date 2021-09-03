from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from service_catalog.models import JobTemplate
from service_catalog.serializers.job_template_serializer import JobTemplateSerializer


class JobTemplateList(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = JobTemplate.objects.all()
    serializer_class = JobTemplateSerializer


class JobTemplateDetails(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser]
    queryset = JobTemplate.objects.all()
    serializer_class = JobTemplateSerializer

