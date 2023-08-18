from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Squest.utils.squest_api_views import SquestObjectPermissions, SquestGenericAPIView, SquestRetrieveUpdateAPIView
from service_catalog.api.serializers.operation_survey_serializer import TowerSurveyFieldSerializer
from service_catalog.models import Operation
from service_catalog.models.tower_survey_field import TowerSurveyField


class SquestOperationSurveyPermissions(SquestObjectPermissions):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    perms_map = {
        'GET': ['service_catalog.change_operation'],
        'OPTIONS': [],
        'HEAD': [],
        'PUT': ['service_catalog.change_operation'],
    }


class OperationSurveyAPI(SquestRetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, SquestOperationSurveyPermissions]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Operation.objects.none()
        return Operation.objects.filter(service_id=self.kwargs['service_id'])

    def get_survey_field(self, name):
        operation = self.get_object()
        try:
            return operation.tower_survey_fields.get(name=name)
        except TowerSurveyField.DoesNotExist:
            raise NotFound(detail=f"Field name '{name}' not found in operation '{operation}'")

    def validate_name_as_an_id(self, operation_id, name_list):
        """
        the name is unique and correspond to an ID in this context
        """
        for name in name_list:
            self.get_survey_field(name=name)
        return True

    @swagger_auto_schema(responses={200: TowerSurveyFieldSerializer(many=True)})
    def get(self, request, *args, **kwargs):
        operation = self.get_object()
        serializer = TowerSurveyFieldSerializer(TowerSurveyField.objects.filter(operation=operation), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: TowerSurveyFieldSerializer(many=True)})
    def put(self, request, *args, **kwargs):
        operation = self.get_object()
        data = request.data
        names = [field['name'] for field in data]
        self.validate_name_as_an_id(operation_id=operation.id, name_list=names)
        instances = []
        for tower_survey_field in data:
            obj = self.get_survey_field(name=tower_survey_field['name'])
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
