from django_celery_results.models import TaskResult
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from service_catalog.api.serializers import TaskResultSerializer


class CeleryTaskView(APIView):

    permission_classes = [IsAdminUser]

    @swagger_auto_schema(responses={200: TaskResultSerializer()})
    def get(self, request, task_id):
        task_result = get_object_or_404(TaskResult, id=task_id)
        serialized_task = TaskResultSerializer(task_result)
        return Response(serialized_task.data, status=status.HTTP_200_OK)
