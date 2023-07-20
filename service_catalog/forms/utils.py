import logging

from django.forms import CharField, TextInput, Textarea, PasswordInput, ChoiceField, Select, MultipleChoiceField, \
    SelectMultiple, IntegerField, NumberInput, FloatField, Field

from Squest.utils.plugin_controller import PluginController

logger = logging.getLogger(__name__)


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


def _get_field_group(field_name, operation_survey):
    all_fields_for_admin = operation_survey.filter(is_customer_field=False).count() == operation_survey.all().count()
    if all_fields_for_admin:
        return "2. Admin fields"
    all_fields_for_user = operation_survey.filter(is_customer_field=True).count() == operation_survey.all().count()
    if all_fields_for_user:
        return "2. User fields"

    if operation_survey.get(name=field_name).is_customer_field:
        return "3. User fields"
    else:
        return "2. Admin fields"


def get_choices_as_tuples_list(choices, default=None):
    if default is None:
        default = [('', "Select an option")]
    if not isinstance(choices, list):
        choices = choices.splitlines()
    return default + [(choice, choice) for choice in choices]


def get_fields_from_survey(survey, tower_survey_fields=None, form_title="2. Service fields", list_disabled_field=None):
    if not list_disabled_field:
        list_disabled_field = list()
    fields = {}
    for survey_field in survey["spec"]:
        disabled = survey_field["variable"] in list_disabled_field
        if survey_field["type"] == "text":
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
            fields[survey_field['variable']] = SquestCharField(
                disabled=disabled,
                label=survey_field['question_name'],
                required=survey_field['required'],
                help_text=survey_field['question_description'],
                min_length=survey_field['min'],
                max_length=survey_field['max'],
                widget=PasswordInput(render_value=True, attrs={'class': 'form-control'}),
                quota=survey_field['quota']
            )

        elif survey_field["type"] == "multiplechoice":
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
            fields[survey_field['variable']] = SquestIntegerField(
                disabled=disabled,
                label=survey_field['question_name'],
                initial=None if not survey_field['default'] else int(survey_field['default']),
                required=survey_field['required'],
                help_text=survey_field['question_description'],
                min_value=None if not survey_field['min'] else int(survey_field['min']),
                max_value=None if not survey_field['max'] else int(survey_field['max']),
                widget=NumberInput(attrs={'class': 'form-control'}),
                quota=survey_field['quota']
            )

        elif survey_field["type"] == "float":
            fields[survey_field['variable']] = SquestFloatField(
                disabled=disabled,
                label=survey_field['question_name'],
                initial=None if not survey_field['default'] else float(survey_field['default']),
                required=survey_field['required'],
                help_text=survey_field['question_description'],
                min_value=None if not survey_field['min'] else float(survey_field['min']),
                max_value=None if not survey_field['max'] else float(survey_field['max']),
                widget=NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
                quota=survey_field['quota']
            )

        if survey_field["validators"] is not None and len(survey_field["validators"]) > 0:
            list_validator_def = list()
            for validator_file in survey_field["validators"]:
                # load dynamically the user provided validator
                loaded_class_plugin = PluginController.get_ui_field_validator_def(validator_file)
                if loaded_class_plugin is not None:
                    list_validator_def.append(loaded_class_plugin)
                    logger.info(f"[Form utils] User validator plugin loaded: {validator_file}")
            fields[survey_field['variable']].validators = list_validator_def

        if tower_survey_fields:
            fields[survey_field['variable']].group = _get_field_group(field_name=survey_field['variable'],
                                                                      operation_survey=tower_survey_fields)
    if fields and form_title != "":
        fields[next(iter(fields))].separator = True
        fields[next(iter(fields))].form_title = form_title
    return fields
