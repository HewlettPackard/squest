from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from service_catalog.models import JobTemplate
from service_catalog.serializers.job_template_serializer import JobTemplateSerializer


@api_view(['GET'])
def fix_ask_variables_on_launch(request, pk):
    job_template = get_object_or_404(JobTemplate, id=pk)
    job_template.set_ask_variables_on_launch(True)
    job_template.push_ask_variables_on_launch()
    return Response(JobTemplateSerializer(job_template).data)
