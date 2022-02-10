from rest_framework.fields import IntegerField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer
from service_catalog.models import Service, JobTemplate


class ServiceSerializer(ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'
        read_only = True


class AdminServiceSerializer(ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class CreateServiceSerializer(ModelSerializer):
    class Meta:
        model = Service
        fields = ['name', 'description', 'image', 'billing_group_id', 'billing_group_is_shown',
                  'billing_group_is_selectable', 'billing_groups_are_restricted', 'enabled', 'job_template',
                  'job_template_timeout']

    job_template = PrimaryKeyRelatedField(label='job template', required=True, queryset=JobTemplate.objects.all(),
                                          help_text="Job template id")

    job_template_timeout = IntegerField(required=False, default=60)

    def save(self):
        job_template_timeout = self.validated_data.get('job_template_timeout', None)
        job_template = self.validated_data.get('job_template', None)
        new_service = Service.objects.create(
            name=self.validated_data.get('name', None),
            description=self.validated_data.get('description', None),
            image=self.validated_data.get('image', None),
            billing_group_id=self.validated_data.get('billing_group_id', None),
            billing_group_is_shown=self.validated_data.get('billing_group_is_shown', None),
            billing_group_is_selectable=self.validated_data.get('billing_group_is_selectable', None),
            billing_groups_are_restricted=self.validated_data.get('billing_groups_are_restricted', None),
            enabled=self.validated_data.get('enabled', None)
        )
        new_service.create_provisioning_operation(job_template, job_template_timeout)
        return new_service
