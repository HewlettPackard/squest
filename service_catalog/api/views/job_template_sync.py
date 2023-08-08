from django_celery_results.models import TaskResult
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from service_catalog import tasks
from service_catalog.api.serializers import TaskResultSerializer
from service_catalog.models import AnsibleController, JobTemplate


class JobTemplateSync(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={202: TaskResultSerializer()})
    def post(self, request, ansible_controller_id, job_template_id=None):
        # get object to check that they exist before sending them to Celery
        ansible_controller = get_object_or_404(AnsibleController, id=ansible_controller_id)
        if not request.user.has_perm('service_catalog.sync_ansiblecontroller', ansible_controller):
            raise PermissionDenied
        if job_template_id is not None:
            queryset = JobTemplate.objects.filter(id=job_template_id, ansible_controller=ansible_controller.id)
            get_object_or_404(queryset)

        task = tasks.ansiblecontroller_sync.delay(ansible_controller.id, job_template_id)
        task_result = TaskResult(task_id=task.task_id)
        task_result.save()
        serialized_task = TaskResultSerializer(task_result)

        return Response(serialized_task.data, status=status.HTTP_202_ACCEPTED)
