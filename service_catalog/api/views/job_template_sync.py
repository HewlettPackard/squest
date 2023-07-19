from django_celery_results.models import TaskResult
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from service_catalog import tasks
from service_catalog.models import TowerServer, JobTemplate
from service_catalog.api.serializers import TaskResultSerializer


class JobTemplateSync(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={202: TaskResultSerializer()})
    def post(self, request, tower_server_id, job_template_id=None):
        # get object to check that they exist before sending them to Celery
        tower_server = get_object_or_404(TowerServer, id=tower_server_id)
        if not request.user.has_perm('service_catalog.sync_towerserver', tower_server):
            raise PermissionDenied
        if job_template_id is not None:
            queryset = JobTemplate.objects.filter(id=job_template_id, tower_server=tower_server.id)
            get_object_or_404(queryset)

        task = tasks.towerserver_sync.delay(tower_server.id, job_template_id)
        task_result = TaskResult(task_id=task.task_id)
        task_result.save()
        serialized_task = TaskResultSerializer(task_result)

        return Response(serialized_task.data, status=status.HTTP_202_ACCEPTED)
