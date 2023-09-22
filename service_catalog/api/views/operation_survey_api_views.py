from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Squest.utils.squest_api_views import SquestObjectPermissions, SquestGenericAPIView, SquestRetrieveUpdateAPIView
from service_catalog.api.serializers.tower_survey_field_serializer import TowerSurveyFieldSerializer
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
    queryset = Operation.objects.all()

    def get_survey_field(self, variable):
        operation = self.get_object()
        try:
            return operation.tower_survey_fields.get(variable=variable)
        except TowerSurveyField.DoesNotExist:
            raise NotFound(detail=f"Variable '{variable}' not found in operation '{operation}'")

    def validate_variable_as_an_id(self, variable_list):
        """
        the variable is unique and correspond to an ID in this context
        """
        for variable in variable_list:
            self.get_survey_field(variable=variable)
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
        variables = [field['variable'] for field in data]
        self.validate_variable_as_an_id(variable_list=variables)
        instances = []
        for tower_survey_field in data:
            obj = self.get_survey_field(variable=tower_survey_field['variable'])
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
