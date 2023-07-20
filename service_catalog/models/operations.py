from django.core.exceptions import ValidationError
from django.db.models import CharField, ForeignKey, BooleanField, IntegerField, CASCADE, SET_NULL, JSONField
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from Squest.utils.squest_model import SquestModel
from service_catalog.models.job_templates import JobTemplate
from service_catalog.models.operation_type import OperationType
from service_catalog.models.services import Service


class Operation(SquestModel):
    name = CharField(max_length=100, verbose_name="Operation name")
    description = CharField(max_length=500, blank=True, null=True)
    type = CharField(
        max_length=10,
        choices=OperationType.choices,
        default=OperationType.CREATE,
        verbose_name="Operation type"
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

    def __str__(self):
        return f"{self.name} ({self.service})"

    def get_absolute_url(self):
        return reverse(f"service_catalog:operation_edit", args=[self.service.id, self.pk])

    def clean(self):
        if self.extra_vars is None or not isinstance(self.extra_vars, dict):
            raise ValidationError({'extra_vars': _("Please enter a valid JSON. Empty value is {} for JSON.")})

    def update_survey(self):
        if self.job_template is not None:
            spec_list = self.job_template.survey.get("spec", [])
            list_of_field_to_have = [survey_spec["variable"] for survey_spec in spec_list]
            list_current_field = [tower_field.name for tower_field in self.tower_survey_fields.all()]
            to_add = list(set(list_of_field_to_have) - set(list_current_field))
            to_remove = list(set(list_current_field) - set(list_of_field_to_have))

            from service_catalog.models.tower_survey_field import TowerSurveyField
            for field_name in to_add:
                TowerSurveyField.objects.create(name=field_name, is_customer_field=True, operation=self)
            for field_name in to_remove:
                TowerSurveyField.objects.get(name=field_name, operation=self).delete()

    def switch_tower_fields_enable_from_dict(self, dict_of_field):
        for key, enabled in dict_of_field.items():
            field = self.tower_survey_fields.get(name=key)
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
                for survey_field in default_survey["spec"]:
                    TowerSurveyField.objects.create(name=survey_field["variable"],
                                                    is_customer_field=True,
                                                    operation=instance)

    @classmethod
    def update_survey_after_job_template_update(cls, job_template):
        # get all operation that use the target job template
        operations = Operation.objects.filter(job_template=job_template)
        for operation in operations:
            operation.update_survey()


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
