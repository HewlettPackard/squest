from rest_framework import serializers

from service_catalog.models import JobTemplate


class JobTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTemplate
        fields = ['tower_id', 'name','ask_variables_on_launch']
        read_only_fields = ['tower_id', 'name']
