from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from service_catalog.api.serializers.operation_survey_serializer import TowerSurveyFieldSerializer
from service_catalog.models import Operation
from service_catalog.models.tower_survey_field import TowerSurveyField


class OperationSurveyAPI(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get_object(operation_id, obj_name):
        try:
            return TowerSurveyField.objects.get(name=obj_name, operation_id=operation_id)
        except TowerSurveyField.DoesNotExist:
            raise NotFound(detail=f"Field name '{obj_name}' not found in operation id '{operation_id}'")

    def validate_name_as_an_id(self, operation_id, name_list):
        """
        the name is unique and correspond to an ID in this context
        """
        for name in name_list:
            self.get_object(operation_id=operation_id, obj_name=name)
        return True

    @swagger_auto_schema(responses={200: TowerSurveyFieldSerializer(many=True)})
    def get(self, request, service_id, pk):
        operation = get_object_or_404(Operation, pk=pk, service__id=service_id)
        if not request.user.has_perm('service_catalog.change_operation', operation):
            raise PermissionDenied
        serializer = TowerSurveyFieldSerializer(TowerSurveyField.objects.filter(operation=operation), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: TowerSurveyFieldSerializer(many=True)})
    def put(self, request, service_id, pk, *args, **kwargs):
        operation = get_object_or_404(Operation, pk=pk, service__id=service_id)
        if not request.user.has_perm('service_catalog.change_operation', operation):
            raise PermissionDenied
        data = request.data
        names = [field['name'] for field in data]
        self.validate_name_as_an_id(operation_id=operation.id, name_list=names)
        instances = []
        for tower_survey_field in data:
            obj = self.get_object(operation_id=operation.id, obj_name=tower_survey_field['name'])
            serializer = TowerSurveyFieldSerializer(instance=obj, data=tower_survey_field, partial=True)
            if serializer.is_valid():
                obj.is_customer_field = tower_survey_field['is_customer_field']
                obj.default = tower_survey_field['default']
                if "validators" in tower_survey_field:
                    obj.validators = tower_survey_field['validators']
                obj.save()
                instances.append(obj)
            else:
                return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)
        serializer = TowerSurveyFieldSerializer(instances, many=True)
        return Response(serializer.data)
