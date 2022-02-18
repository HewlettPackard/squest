from rest_framework.serializers import ModelSerializer

from service_catalog.models.tower_survey_field import TowerSurveyField


class TowerSurveyFieldSerializer(ModelSerializer):

    class Meta:
        model = TowerSurveyField
        fields = ('name', 'enabled', 'default')
        read_only_fields = ('name',)
