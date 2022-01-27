from rest_framework import serializers

from service_catalog.models import JobTemplate


class JobTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTemplate
        fields = '__all__'
        read_only_fields = ['tower_id', 'tower_server', 'survey', 'tower_job_template_data']
