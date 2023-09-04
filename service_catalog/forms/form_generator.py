import copy
import logging

from django.core.exceptions import ValidationError
from django.forms import CharField, TextInput, Textarea, PasswordInput, ChoiceField, Select, MultipleChoiceField, \
    SelectMultiple, IntegerField, NumberInput, FloatField, Field
from rest_framework.serializers import ChoiceField as DjangoRestChoiceField
from rest_framework.serializers import CharField as DjangoRestCharField
from rest_framework.serializers import MultipleChoiceField as DjangoRestMultipleChoiceField
from rest_framework.serializers import IntegerField as DjangoRestIntegerField
from rest_framework.serializers import FloatField as DjangoRestFloatField

from jinja2 import Template
from jinja2.exceptions import UndefinedError

from Squest.utils.plugin_controller import PluginController
from service_catalog.models import ApprovalState

logger = logging.getLogger(__name__)


def get_choices_as_tuples_list(choices, default=None):
    if default is None:
        default = [('', "Select an option")]
    if not isinstance(choices, list):
        choices = choices.splitlines()
    return default + [(choice, choice) for choice in choices]


class SquestField(Field):
    def __init__(self, quota=None, *args, **kwargs):
        self.quota = quota
        super().__init__(*args, **kwargs)


class SquestIntegerField(SquestField, IntegerField):
    pass


class SquestCharField(SquestField, CharField):
    pass


class SquestChoiceField(SquestField, ChoiceField):
    pass


class SquestMultipleChoiceField(SquestField, MultipleChoiceField):
    pass


class SquestFloatField(SquestField, FloatField):
    pass


class FormGenerator:

    def __init__(self, user, operation=None, squest_request=None, squest_instance=None, is_api_form=False, quota_scope=None):
        self.user = user
        self.operation = operation
        self.squest_request = squest_request
        self.squest_instance = squest_instance
        self.is_api_form = is_api_form
        self.is_initial_form = False
        self.quota_scope = quota_scope
        if self.quota_scope is None:
            # try to get the quota scope from the instance
            if self.squest_request is not None:
                self.quota_scope = self.squest_request.instance.quota_scope
            elif self.squest_instance is not None:
                self.quota_scope = self.squest_instance.quota_scope
        if (self.operation and not self.squest_request and not self.squest_instance) or (self.operation and self.squest_instance):
            self.is_initial_form = True
        if self.operation is None:
            self.operation = self.squest_request.operation
        self.survey_as_dict = copy.copy(self.operation.job_template.survey)

    def generate_form(self):
        if not self.operation.job_template.has_a_survey():
            # empty survey, no fields to generate
            return {}
        if self.is_initial_form:
            # get all field that are not disabled by the admin
            self._get_customer_field_only()
        if self.squest_request and self.squest_request.approval_workflow_state:
            self._get_field_from_approval_step()

        self._apply_jinja_template_to_survey()
        self._apply_user_validator_to_survey()
        if self.quota_scope is not None:
            self._apply_quota_to_survey()

        django_form = self._get_django_fields_from_survey()

        if self.squest_request:
            # this is an admin accept form
            django_form = self._prefill_form_with_customer_values(django_form)

        if self.squest_request and self.squest_request.approval_workflow_state:
            # this is an approval step accept form
            django_form = self._override_form_fields_with_previous_step_values(django_form)
        return django_form

    def _get_customer_field_only(self):
        """
        Return survey fields from the job template that are active in the operation
        :return: survey dict
        :rtype dict
        """
        # copy the dict from the job template survey
        new_survey = copy.copy(self.operation.job_template.survey)
        # cleanup the list
        new_survey["spec"] = list()
        # loop the original survey
        for survey_filled in self.survey_as_dict['spec']:
            target_tower_field = self.operation.tower_survey_fields.get(name=survey_filled["variable"])
            if target_tower_field.is_customer_field:
                new_survey["spec"].append(survey_filled)
        self.survey_as_dict = new_survey

    def _apply_jinja_template_to_survey(self):
        """
        Apply the "default" field of the operation survey
        :return: Updated survey with templated string from spec
        """
        if self.squest_request is None and self.squest_instance is None:
            return
        if self.squest_request and self.squest_request.instance:
            instance = self.squest_request.instance
        else:
            instance = self.squest_instance
        from service_catalog.api.serializers import InstanceSerializer
        from profiles.api.serializers import UserSerializer
        context = {
            "user": UserSerializer(self.user).data,
            "instance": InstanceSerializer(instance).data
        }
        for survey_filled in self.survey_as_dict.get("spec", []):   # loop all survey config from tower
            target_tower_field = self.operation.tower_survey_fields.get(name=survey_filled["variable"])
            # jinja templating default values
            if target_tower_field.default is not None and target_tower_field.default != "":
                survey_filled["default"] = self._template_field(target_tower_field.default, context)

    def _apply_user_validator_to_survey(self):
        for survey_filled in self.survey_as_dict.get("spec", []):  # loop all survey config from tower
            target_tower_field = self.operation.tower_survey_fields.get(name=survey_filled["variable"])
            survey_filled["validators"] = list()
            if target_tower_field.validators is not None:
                survey_filled["validators"] = target_tower_field.validators.split(",")

    def _apply_quota_to_survey(self):
        for survey_filled in self.survey_as_dict.get("spec", []):  # loop all survey config from tower
            target_tower_field = self.operation.tower_survey_fields.get(name=survey_filled["variable"])
            survey_filled["quota"] = None
            if target_tower_field.attribute_definition:
                quota_string = target_tower_field.attribute_definition.name
                # by default, we only show the impacted quota
                survey_filled["quota"] = quota_string
                # get the quota scope
                quota_scope_quota = self.quota_scope.quotas.filter(attribute_definition=target_tower_field.attribute_definition)
                if quota_scope_quota.exists():
                    quota_scope_quota = quota_scope_quota.first()
                    survey_filled["max"] = quota_scope_quota.available
                    quota_string += f" - available: {quota_scope_quota.available}"
                survey_filled["quota"] = quota_string

    def _template_field(self, jinja_template_string, template_data_dict):
        """
        Template a field value with user and or admin spec
        :param jinja_template_string: string that may contain jinja template markers
        :param template_data_dict: dict context
        :return: templated string
        """
        if template_data_dict is None:
            template_data_dict = dict()
        templated_string = ""
        template = Template(jinja_template_string)
        try:
            templated_string = template.render(template_data_dict)
        except UndefinedError as e:
            logger.warning(f"[template_field] templating error: {e.message}")
            pass
        return templated_string

    def _get_field_from_approval_step(self):
        # copy the dict
        new_survey = copy.copy(self.survey_as_dict)
        # cleanup the list
        new_survey["spec"] = list()
        # loop the original survey
        for survey_filled in self.survey_as_dict.get("spec", []):
            # Readable fields
            if survey_filled["variable"] in [tower_field.name for tower_field
                                             in self.squest_request.approval_workflow_state.current_step.approval_step.readable_fields.all()]:
                new_field = copy.copy(survey_filled)
                new_field["disabled"] = True
                new_field["required"] = False
                new_survey["spec"].append(new_field)
            # Writable fields
            if survey_filled["variable"] in [tower_field.name for tower_field in self.squest_request.approval_workflow_state.current_step.approval_step.editable_fields.all()]:
                new_field = copy.copy(survey_filled)
                new_field["disabled"] = False
                new_survey["spec"].append(new_field)
        self.survey_as_dict = new_survey

    def _prefill_form_with_customer_values(self, django_form: dict):
        for field in django_form.keys():
            if field in self.squest_request.fill_in_survey:
                django_form.get(field).initial = self.squest_request.fill_in_survey[field]
                django_form.get(field).default = self.squest_request.fill_in_survey[field]
            if field in self.squest_request.admin_fill_in_survey:
                django_form.get(field).initial = self.squest_request.admin_fill_in_survey[field]
                django_form.get(field).default = self.squest_request.admin_fill_in_survey[field]
        return django_form

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

    def _get_django_fields_from_survey(self):
        fields = {}
        for survey_field in self.survey_as_dict["spec"]:
            disabled = survey_field.get("disabled", False)
            if survey_field["type"] == "text":
                if self.is_api_form:
                    fields[survey_field['variable']] = DjangoRestCharField(
                        label=survey_field['question_name'],
                        initial=survey_field['default'],
                        required=survey_field['required'],
                        help_text=survey_field['question_description'],
                        min_length=survey_field['min'],
                        max_length=survey_field['max']
                    )
                else:
                    fields[survey_field['variable']] = SquestCharField(
                        disabled=disabled,
                        label=survey_field['question_name'],
                        initial=survey_field['default'],
                        required=survey_field['required'],
                        help_text=survey_field['question_description'],
                        min_length=survey_field['min'],
                        max_length=survey_field['max'],
                        widget=TextInput(attrs={'class': 'form-control'}),
                        quota=survey_field['quota']
                    )

            elif survey_field["type"] == "textarea":
                if self.is_api_form:
                    fields[survey_field['variable']] = DjangoRestCharField(
                        label=survey_field['question_name'],
                        initial=survey_field['default'],
                        required=survey_field['required'],
                        help_text=survey_field['question_description'],
                        min_length=survey_field['min'],
                        max_length=survey_field['max']
                    )
                else:
                    fields[survey_field['variable']] = SquestCharField(
                        disabled=disabled,
                        label=survey_field['question_name'],
                        initial=survey_field['default'],
                        required=survey_field['required'],
                        help_text=survey_field['question_description'],
                        min_length=survey_field['min'],
                        max_length=survey_field['max'],
                        widget=Textarea(attrs={'class': 'form-control'}),
                        quota=survey_field['quota']
                    )
            elif survey_field["type"] == "password":
                if self.is_api_form:
                    fields[survey_field['variable']] = DjangoRestCharField(
                        label=survey_field['question_name'],
                        required=survey_field['required'],
                        help_text=survey_field['question_description'],
                        min_length=survey_field['min'],
                        max_length=survey_field['max'],
                        initial=survey_field['default'],
                    )
                else:
                    fields[survey_field['variable']] = SquestCharField(
                        disabled=disabled,
                        label=survey_field['question_name'],
                        required=survey_field['required'],
                        help_text=survey_field['question_description'],
                        min_length=survey_field['min'],
                        max_length=survey_field['max'],
                        widget=PasswordInput(render_value=True, attrs={'class': 'form-control'}),
                        quota=survey_field['quota'],
                        initial=survey_field['default']
                    )

            elif survey_field["type"] == "multiplechoice":
                if self.is_api_form:
                    fields[survey_field['variable']] = DjangoRestChoiceField(
                        label=survey_field['question_name'],
                        initial=survey_field['default'],
                        required=survey_field['required'],
                        help_text=survey_field['question_description'],
                        choices=get_choices_as_tuples_list(survey_field["choices"]),
                        error_messages={'required': 'At least you must select one choice'}
                    )
                else:
                    fields[survey_field['variable']] = SquestChoiceField(
                        disabled=disabled,
                        label=survey_field['question_name'],
                        initial=survey_field['default'],
                        required=survey_field['required'],
                        help_text=survey_field['question_description'],
                        choices=get_choices_as_tuples_list(survey_field["choices"]),
                        error_messages={'required': 'At least you must select one choice'},
                        widget=Select(attrs={'class': 'form-control selectpicker', 'data-live-search': 'true'}),
                        quota=survey_field['quota']
                    )

            elif survey_field["type"] == "multiselect":
                if self.is_api_form:
                    fields[survey_field['variable']] = DjangoRestMultipleChoiceField(
                        label=survey_field['question_name'],
                        initial=survey_field['default'].split("\n"),
                        required=survey_field['required'],
                        help_text=survey_field['question_description'],
                        choices=get_choices_as_tuples_list(survey_field["choices"]),
                    )
                else:
                    fields[survey_field['variable']] = SquestMultipleChoiceField(
                        disabled=disabled,
                        label=survey_field['question_name'],
                        initial=survey_field['default'].split("\n"),
                        required=survey_field['required'],
                        help_text=survey_field['question_description'],
                        choices=get_choices_as_tuples_list(survey_field["choices"], []),
                        widget=SelectMultiple(attrs={'class': 'form-control selectpicker', 'data-live-search': 'true'}),
                        quota=survey_field['quota']
                    )

            elif survey_field["type"] == "integer":
                if self.is_api_form:
                    fields[survey_field['variable']] = DjangoRestIntegerField(
                        label=survey_field['question_name'],
                        initial=0 if not survey_field['default'] else int(survey_field['default']),
                        required=survey_field['required'],
                        help_text=survey_field['question_description'],
                        min_value=self.cast_integer_or_default(survey_field['min']),
                        max_value=self.cast_integer_or_default(survey_field['max']),
                    )
                else:
                    fields[survey_field['variable']] = SquestIntegerField(
                        disabled=disabled,
                        label=survey_field['question_name'],
                        initial=None if not survey_field['default'] else int(survey_field['default']),
                        required=survey_field['required'],
                        help_text=survey_field['question_description'],
                        min_value=self.cast_integer_or_default(survey_field['min']),
                        max_value=self.cast_integer_or_default(survey_field['max']),
                        widget=NumberInput(attrs={'class': 'form-control'}),
                        quota=survey_field['quota']
                    )

            elif survey_field["type"] == "float":
                if self.is_api_form:
                    fields[survey_field['variable']] = DjangoRestFloatField(
                        label=survey_field['question_name'],
                        initial=0 if not survey_field['default'] else float(survey_field['default']),
                        required=survey_field['required'],
                        help_text=survey_field['question_description'],
                        min_value=self.cast_float_or_default(survey_field['min']),
                        max_value=self.cast_float_or_default(survey_field['max']),
                    )
                else:
                    fields[survey_field['variable']] = SquestFloatField(
                        disabled=disabled,
                        label=survey_field['question_name'],
                        initial=None if not survey_field['default'] else float(survey_field['default']),
                        required=survey_field['required'],
                        help_text=survey_field['question_description'],
                        min_value=self.cast_float_or_default(survey_field['min']),
                        max_value=self.cast_float_or_default(survey_field['max']),
                        widget=NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
                        quota=survey_field['quota']
                    )

            if survey_field["validators"] is not None and len(survey_field["validators"]) > 0:
                list_validator_def = list()
                for validator_file in survey_field["validators"]:
                    # load dynamically the user provided validator
                    if self.is_api_form:
                        loaded_class_plugin = PluginController.get_api_field_validator_def(validator_file)
                    else:
                        loaded_class_plugin = PluginController.get_ui_field_validator_def(validator_file)
                    if loaded_class_plugin is not None:
                        list_validator_def.append(loaded_class_plugin)
                        logger.info(f"[Form utils] User validator plugin loaded: {validator_file}")
                fields[survey_field['variable']].validators = list_validator_def

        return fields

    def _override_form_fields_with_previous_step_values(self, django_form):
        for step in self.squest_request.approval_workflow_state.approval_step_states.order_by(
                'approval_step__position'):
            if step.state == ApprovalState.APPROVED:
                for field, value in step.fill_in_survey.items():
                    django_field = django_form.get(field)
                    if django_field:
                        django_field.initial = value
                        django_field.default = value
        return django_form
