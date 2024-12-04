import logging
import sys

from django.db.models import CharField, BooleanField, ForeignKey, CASCADE, SET_NULL, JSONField, IntegerField
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.forms import CharField as FormsCharField
from django.forms import ChoiceField as FormsChoiceField
from django.forms import FloatField as FormsFloatField
from django.forms import IntegerField as FormsIntegerField
from django.forms import MultipleChoiceField as FormsMultipleChoiceField
from django.forms import NumberInput as FormsNumberInput
from django.forms import PasswordInput as FormsPasswordInput
from django.forms import Select as FormsSelect
from django.forms import SelectMultiple as FormsSelectMultiple
from django.forms import TextInput as FormsTextInput
from django.forms import Textarea as FormsTextarea
from jinja2 import Template, Environment
from jinja2.exceptions import UndefinedError
from rest_framework.serializers import CharField as DjangoRestCharField
from rest_framework.serializers import ChoiceField as DjangoRestChoiceField
from rest_framework.serializers import FloatField as DjangoRestFloatField
from rest_framework.serializers import IntegerField as DjangoRestIntegerField
from rest_framework.serializers import MultipleChoiceField as DjangoRestMultipleChoiceField

from Squest.utils.plugin_controller import PluginController
from Squest.utils.squest_model import SquestModel
from resource_tracker_v2.models import AttributeDefinition
from service_catalog.models import Operation
import json

logger = logging.getLogger(__name__)

custom_filters = {
    "to_json": lambda value: json.dumps(value, indent=2),  # Convert to JSON
}

# Initialize Jinja2 environment
custom_env = Environment()

# Dynamically add filters
for filter_name, filter_func in custom_filters.items():
    custom_env.filters[filter_name] = filter_func


def get_choices_as_tuples_list(choices, default=None):
    if default is None:
        default = [('', "Select an option")]
    if not isinstance(choices, list):
        choices = choices.splitlines()
    return default + [(choice, choice) for choice in choices]


class SquestIntegerField(FormsIntegerField):
    def __init__(self, quota=None, *args, **kwargs):
        self.quota = quota
        super().__init__(*args, **kwargs)


class TowerSurveyField(SquestModel):
    class Meta(SquestModel.Meta):
        unique_together = ('operation', 'variable')
        ordering = ('position',)

    variable = CharField(null=False, blank=False, max_length=200)
    position = IntegerField(default=0)
    is_customer_field = BooleanField(default=True, null=False, blank=False, help_text="Display for non approver user")
    default = CharField(null=True, blank=True, max_length=200, verbose_name="Default value")
    operation = ForeignKey(Operation,
                           on_delete=CASCADE,
                           related_name="tower_survey_fields",
                           related_query_name="tower_survey_field")
    validators = CharField(null=True, blank=True, max_length=200, verbose_name="Field validators")
    attribute_definition = ForeignKey(AttributeDefinition,
                                      null=True, blank=True,
                                      on_delete=SET_NULL,
                                      related_name="tower_survey_fields",
                                      related_query_name="tower_survey_field")
    type = CharField(max_length=50)
    required = BooleanField()
    name = CharField(max_length=200)
    description = CharField(max_length=500)
    field_options = JSONField()

    def __str__(self):
        return self.name

    def templating_default(self, instance, user):
        """
        Template a field value with user and or admin spec
        :param jinja_template_string: string that may contain jinja template markers
        :param template_data_dict: dict context
        :return: templated string
        """
        default_value = self.field_options.get('default')
        if self.default is None:
            return default_value

        # Use the custom environment to create a Template
        template = custom_env.from_string(self.default)
        from service_catalog.api.serializers import InstanceSerializer
        from profiles.api.serializers import UserSerializer
        context = {
            "user": UserSerializer(user).data,
            "instance": InstanceSerializer(instance).data
        }
        try:
            default_value = template.render(context)
        except UndefinedError as e:
            logger.warning(f"[template_field] templating error: {e.message}")
            pass
        return default_value

    def get_available_quota(self, quota_scope):
        # Quota is mandatory in instance may be it is dead code
        if quota_scope is not None:
            quota_scope_quota = quota_scope.quotas.filter(attribute_definition=self.attribute_definition)
            if quota_scope_quota.exists():
                quota_scope_quota = quota_scope_quota.first()
                return quota_scope_quota.available
        return None

    def get_field(self, quota_scope, instance, user, is_api=False, disabled=False):
        default = self.templating_default(instance, user)
        required = self.required if not disabled else False
        if self.type == "text":
            if is_api:
                field = DjangoRestCharField(
                    label=self.name,
                    initial=default,
                    required=required,
                    help_text=self.description,
                    min_length=self.field_options['min'],
                    max_length=self.field_options['max']
                )
            else:
                field = FormsCharField(
                    disabled=disabled,
                    label=self.name,
                    initial=default,
                    required=required,
                    help_text=self.description,
                    min_length=self.field_options['min'],
                    max_length=self.field_options['max'],
                    widget=FormsTextInput(attrs={'class': 'form-control'}),
                )
        elif self.type == "textarea":
            if is_api:
                field = DjangoRestCharField(
                    label=self.name,
                    initial=default,
                    required=required,
                    help_text=self.description,
                    min_length=self.field_options['min'],
                    max_length=self.field_options['max']
                )
            else:
                field = FormsCharField(
                    disabled=disabled,
                    label=self.name,
                    initial=default,
                    required=required,
                    help_text=self.description,
                    min_length=self.field_options['min'],
                    max_length=self.field_options['max'],
                    widget=FormsTextarea(attrs={'class': 'form-control'}),
                )
        elif self.type == "password":
            if is_api:
                field = DjangoRestCharField(
                    label=self.name,
                    required=required,
                    help_text=self.description,
                    min_length=self.field_options['min'],
                    max_length=self.field_options['max'],
                    initial=default,
                )
            else:
                field = FormsCharField(
                    disabled=disabled,
                    label=self.name,
                    required=required,
                    help_text=self.description,
                    min_length=self.field_options['min'],
                    max_length=self.field_options['max'],
                    widget=FormsPasswordInput(render_value=True, attrs={'class': 'form-control'}),
                    initial=default
                )

        elif self.type == "multiplechoice":
            if is_api:
                field = DjangoRestChoiceField(
                    label=self.name,
                    initial=default,
                    required=required,
                    help_text=self.description,
                    choices=get_choices_as_tuples_list(self.field_options['choices']),
                    error_messages={'required': 'At least you must select one choice'}
                )
            else:
                field = FormsChoiceField(
                    disabled=disabled,
                    label=self.name,
                    initial=default,
                    required=required,
                    help_text=self.description,
                    choices=get_choices_as_tuples_list(self.field_options['choices'], []),
                    error_messages={'required': 'At least you must select one choice'},
                    widget=FormsSelect(attrs={'class': 'form-control selectpicker', 'data-live-search': 'true'}),
                )

        elif self.type == "multiselect":
            if is_api:
                field = DjangoRestMultipleChoiceField(
                    label=self.name,
                    initial=default.split("\n"),
                    required=required,
                    help_text=self.description,
                    choices=get_choices_as_tuples_list(self.field_options['choices']),
                )
            else:
                field = FormsMultipleChoiceField(
                    disabled=disabled,
                    label=self.name,
                    initial=default.split("\n"),
                    required=required,
                    help_text=self.description,
                    choices=get_choices_as_tuples_list(self.field_options['choices'], []),
                    widget=FormsSelectMultiple(
                        attrs={'class': 'form-control selectpicker', 'data-live-search': 'true'}),
                )

        elif self.type == "integer":
            available_quota = self.get_available_quota(quota_scope)
            quota_str = f"{self.attribute_definition.name} - available {available_quota}" if self.attribute_definition else None
            if is_api:
                field = DjangoRestIntegerField(
                    label=self.name,
                    initial=0 if not default else int(default),
                    required=required,
                    help_text=self.description,
                    min_value=self.cast_integer_or_default(self.field_options['min']),
                    max_value=self.get_maximum_value(available_quota, self.field_options.get('max')),
                )
            else:
                field = SquestIntegerField(
                    disabled=disabled,
                    label=self.name,
                    initial=None if not default else int(default),
                    required=required,
                    help_text=self.description,
                    min_value=self.cast_integer_or_default(self.field_options['min']),
                    max_value=self.get_maximum_value(available_quota, self.field_options.get('max')),
                    widget=FormsNumberInput(attrs={'class': 'form-control'}),
                    quota=quota_str
                )
        elif self.type == "float":
            if is_api:
                field = DjangoRestFloatField(
                    label=self.name,
                    initial=0 if not default else float(default),
                    required=required,
                    help_text=self.description,
                    min_value=self.cast_float_or_default(self.field_options['min']),
                    max_value=self.cast_float_or_default(self.field_options['max']),
                )
            else:
                field = FormsFloatField(
                    disabled=disabled,
                    label=self.name,
                    initial=None if not default else float(default),
                    required=required,
                    help_text=self.description,
                    min_value=self.cast_float_or_default(self.field_options['min']),
                    max_value=self.cast_float_or_default(self.field_options['max']),
                    widget=FormsNumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
                )
        if self.validators is not None:
            list_validator_def = list()
            for validator_file in self.validators.split(","):
                # load dynamically the user provided validator
                if is_api:
                    loaded_class_plugin = PluginController.get_api_field_validator_def(validator_file)
                else:
                    loaded_class_plugin = PluginController.get_ui_field_validator_def(validator_file)
                if loaded_class_plugin is not None:
                    list_validator_def.append(loaded_class_plugin)
                    logger.info(f"[Form utils] User validator plugin loaded: {validator_file}")
            field.validators = list_validator_def
        return field

    @staticmethod
    def cast_integer_or_default(value, default=None):
        try:
            returned_value = int(value)
        except (ValueError, TypeError):
            returned_value = default
        return returned_value

    @staticmethod
    def cast_float_or_default(value, default=None):
        try:
            returned_value = float(value)
        except (ValueError, TypeError):
            returned_value = default
        return returned_value

    def get_maximum_value(self, available_quota, max_field):
        max_quota = self.cast_integer_or_default(available_quota, sys.maxsize)
        max_survey = self.cast_integer_or_default(max_field, sys.maxsize)
        return min(max_quota, max_survey)


@receiver(pre_save, sender=TowerSurveyField)
def on_change(sender, instance: TowerSurveyField, **kwargs):
    if instance.type != "integer":
        instance.attribute_definition = None
    if instance.id is not None:
        previous = TowerSurveyField.objects.get(id=instance.id)
        if previous.is_customer_field != instance.is_customer_field:
            # update all request that use this tower field survey. Move filled fields between user and admin survey
            for request in instance.operation.request_set.all():
                if instance.variable in request.admin_fill_in_survey.keys() and instance.is_customer_field:
                    old = request.admin_fill_in_survey.pop(instance.variable)
                    request.fill_in_survey[instance.variable] = old
                elif instance.variable in request.fill_in_survey.keys() and not instance.is_customer_field:
                    old = request.fill_in_survey.pop(instance.variable)
                    request.admin_fill_in_survey[instance.variable] = old
                else:
                    logger.warning("[set_field_in_survey] field has not changed")
                request.save()
