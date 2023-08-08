from rest_framework import serializers

from service_catalog.models import JobTemplate


class JobTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTemplate
        fields = '__all__'
        read_only_fields = ['remote_id', 'ansible_controller', 'survey', 'remote_job_template_data']
