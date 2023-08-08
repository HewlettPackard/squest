from rest_framework.serializers import ModelSerializer

from service_catalog.models.survey_field import SurveyField


class TowerSurveyFieldSerializer(ModelSerializer):

    class Meta:
        model = SurveyField
        fields = ('name', 'is_customer_field', 'default', 'validators')
        read_only_fields = ('name',)
