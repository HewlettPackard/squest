from django.core.exceptions import ValidationError
from django.db.models import CharField, ForeignKey, BooleanField, IntegerField, CASCADE, SET_NULL, JSONField
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from Squest.utils.ansible_when import AnsibleWhen
from Squest.utils.plugin_controller import PluginController
from Squest.utils.squest_model import SquestModel
from service_catalog.models.job_templates import JobTemplate
from service_catalog.models.operation_type import OperationType
from service_catalog.models.services import Service


class Operation(SquestModel):
    name = CharField(max_length=100)
    description = CharField(max_length=500, blank=True, null=True)
    type = CharField(
        max_length=10,
        choices=OperationType.choices,
        default=OperationType.CREATE,
    )
    service = ForeignKey(Service, on_delete=CASCADE, related_name="operations",
                         related_query_name="operation")
    job_template = ForeignKey(JobTemplate, null=True, on_delete=SET_NULL)
    auto_accept = BooleanField(default=False, blank=True)
    auto_process = BooleanField(default=False, blank=True)
    process_timeout_second = IntegerField(default=60, verbose_name="Process timeout (s)")
    enabled = BooleanField(default=True, blank=True)
    extra_vars = JSONField(default=dict, blank=True)
    is_admin_operation = BooleanField(default=False, blank=True, verbose_name="Admin operation",
                                      help_text='Create operations are protected by "service_catalog.admin_request_on_service", others by "service_catalog.admin_request_on_instance".')
    default_inventory_id = CharField(max_length=500, blank=True, null=True,
                                     help_text="Jinja supported with context {{ request }}. "
                                               "Id of the inventory to use by default. "
                                               "Leave blank to use the default Job Template inventory")
    default_limits = CharField(max_length=500, blank=True, null=True,
                               help_text="Jinja supported with context {{ request }}. "
                                         "Comma separated list of inventory host limits")
    default_tags = CharField(max_length=500, blank=True, null=True,
                             help_text="Jinja supported. Comma separated list of tags")
    default_skip_tags = CharField(max_length=500, blank=True, null=True,
                                  help_text="Jinja supported. Comma separated list of skip tags")
    default_credentials_ids = CharField(max_length=500, blank=True, null=True,
                                        help_text="Jinja supported with context `{{ request }}`. "
                                                  "Comma separated list of credentials ID")
    default_verbosity = CharField(max_length=500, blank=True, null=True,
                                  help_text="Jinja supported. Verbosity level (Integer)")
    default_diff_mode = CharField(max_length=500, blank=True, null=True,
                                  help_text="Jinja supported. Show changes")
    default_job_type = CharField(max_length=500, blank=True, null=True,
                                 help_text="Jinja supported. Job template type")
    validators = CharField(null=True, blank=True, max_length=200, verbose_name="Survey validators")
    when = CharField(max_length=2000, blank=True, null=True,
                     help_text="Ansible like 'when' with `instance` as context. No Jinja brackets needed. Cannot be set on 'create' type of operation as the instance does not exist yet")

    @property
    def validators_name(self):
        return self.validators.split(",") if self.validators else None

    def get_validators(self):
        validators = list()
        if self.validators is not None:
            all_validators = self.validators_name
            all_validators.sort()
            for validator_file in all_validators:
                validator = PluginController.get_survey_validator_def(validator_file)
                if validator:
                    validators.append(validator)
        return validators

    def __str__(self):
        return f"{self.name} ({self.service})"

    def get_absolute_url(self):
        return reverse(f"service_catalog:operation_details", args=[self.pk])

    def clean(self):
        if self.extra_vars is None or not isinstance(self.extra_vars, dict):
            raise ValidationError({'extra_vars': _("Please enter a valid JSON. Empty value is {} for JSON.")})

    def update_survey(self):
        if self.job_template is not None:
            spec_list = self.job_template.survey.get("spec", [])
            from service_catalog.models.tower_survey_field import TowerSurveyField
            position = 0
            for field in spec_list:
                squest_field, created = TowerSurveyField.objects.get_or_create(
                    variable=field['variable'],
                    operation=self,
                    defaults={
                        'is_customer_field': True,
                        'position': position,
                        'name': field['question_name'],
                        'description': field['question_description'],
                        'type': field['type'],
                        'required': field['required'],
                        'field_options': {
                            'min': field.get('min', ''),
                            'max': field.get('max', ''),
                            'choices': field.get('choices', ''),
                            'default': field.get('default', '')
                        }
                    }
                )
                if not created:
                    squest_field.name = field['question_name']
                    squest_field.position = position
                    squest_field.description = field['question_description']
                    squest_field.type = field['type']
                    squest_field.required = field['required']
                    squest_field.field_options = {
                        "min": field.get('min', ''),
                        "max": field.get('max', ''),
                        "choices": field.get('choices', ''),
                        "default": field.get('default', '')
                    }
                    squest_field.save()
                position += 1
            self.tower_survey_fields.exclude(
                variable__in=[survey_spec["variable"] for survey_spec in spec_list]).delete()

    def switch_tower_fields_enable_from_dict(self, dict_of_field):
        for key, enabled in dict_of_field.items():
            field = self.tower_survey_fields.get(variable=key)
            field.is_customer_field = enabled
            field.save()

    @classmethod
    def add_job_template_survey_as_default_survey(cls, sender, instance, created, *args, **kwargs):
        from service_catalog.models.tower_survey_field import TowerSurveyField
        if created:
            if instance.type == OperationType.CREATE and instance.service:
                instance.service.enabled = True
                instance.service.save()
            # copy the default survey and add a flag 'is_visible'
            default_survey = instance.job_template.survey
            if "spec" in default_survey:
                position = 0
                for field in default_survey["spec"]:
                    TowerSurveyField.objects.create(
                        variable=field['variable'],
                        position=position,
                        is_customer_field=True,
                        operation=instance,
                        name=field['question_name'],
                        description=field['question_description'],
                        type=field['type'],
                        required=field['required'],
                        field_options={
                            "min": field.get('min', ''),
                            "max": field.get('max', ''),
                            "choices": field.get('choices', ''),
                            "default": field.get('default', '')
                        }
                    )
                    position += 1


    def when_instance_authorized(self, instance):
        from service_catalog.api.serializers import InstanceSerializer
        if not self.when:
            return True
        when_context = {
            "instance": InstanceSerializer(instance).data
        }
        return AnsibleWhen.when_render(context=when_context, when_string=self.when)

post_save.connect(Operation.add_job_template_survey_as_default_survey, sender=Operation)


@receiver(pre_save, sender=Operation)
def on_change(sender, instance: Operation, **kwargs):
    if instance.id is not None:
        previous = Operation.objects.get(id=instance.id)
        if previous.job_template != instance.job_template:
            instance.update_survey()
        if instance.type == OperationType.CREATE and instance.enabled and previous.enabled != instance.enabled and instance.service.can_be_enabled():
            instance.service.enabled = True
            instance.service.save()


@receiver(post_save, sender=Operation)
def disable_service(sender, instance: Operation, **kwargs):
    # disable the service if no more job template linked or operation is disabled to a create operation
    if instance.type == OperationType.CREATE and not instance.service.can_be_enabled():
        instance.service.enabled = False
        instance.service.save()


@receiver(post_delete, sender=Operation)
def on_delete(sender, instance: Operation, **kwargs):
    # disable the service if no more 'CREATE' operation
    if instance.type == OperationType.CREATE and not instance.service.can_be_enabled():
        instance.service.enabled = False
        instance.service.save()
