import logging

from django.forms import CharField, TextInput, Textarea, PasswordInput, ChoiceField, Select, MultipleChoiceField, \
    SelectMultiple, IntegerField, NumberInput, FloatField

from Squest.utils.plugin_controller import PluginController

logger = logging.getLogger(__name__)


def _get_field_group(field_name, operation_survey):
    all_fields_for_admin = operation_survey.filter(enabled=False).count() == operation_survey.all().count()
    if all_fields_for_admin:
        return "2. Admin fields"
    all_fields_for_user = operation_survey.filter(enabled=True).count() == operation_survey.all().count()
    if all_fields_for_user:
        return "2. User fields"

    if operation_survey.get(name=field_name).enabled:
        return "3. User fields"
    else:
        return "2. Admin fields"


def get_choices_as_tuples_list(choices, default=None):
    if default is None:
        default = [('', "Select an option")]
    if not isinstance(choices, list):
        choices = choices.splitlines()
    return default + [(choice, choice) for choice in choices]


def get_fields_from_survey(survey, tower_survey_fields=None, form_title="2. Service fields"):
    fields = {}
    for survey_field in survey["spec"]:
        if survey_field["type"] == "text":
            fields[survey_field['variable']] = CharField(
                label=survey_field['question_name'],
                initial=survey_field['default'],
                required=survey_field['required'],
                help_text=survey_field['question_description'],
                min_length=survey_field['min'],
                max_length=survey_field['max'],
                widget=TextInput(
                    attrs={'class': 'form-control'}
                )
            )

        elif survey_field["type"] == "textarea":
            fields[survey_field['variable']] = CharField(
                label=survey_field['question_name'],
                initial=survey_field['default'],
                required=survey_field['required'],
                help_text=survey_field['question_description'],
                min_length=survey_field['min'],
                max_length=survey_field['max'],
                widget=Textarea(
                    attrs={'class': 'form-control'}
                )
            )

        elif survey_field["type"] == "password":
            fields[survey_field['variable']] = CharField(
                label=survey_field['question_name'],
                required=survey_field['required'],
                help_text=survey_field['question_description'],
                min_length=survey_field['min'],
                max_length=survey_field['max'],
                widget=PasswordInput(render_value=True, attrs={'class': 'form-control'}
                                     )
            )

        elif survey_field["type"] == "multiplechoice":
            fields[survey_field['variable']] = ChoiceField(
                label=survey_field['question_name'],
                initial=survey_field['default'],
                required=survey_field['required'],
                help_text=survey_field['question_description'],
                choices=get_choices_as_tuples_list(survey_field["choices"]),
                error_messages={'required': 'At least you must select one choice'},
                widget=Select(
                    attrs={'class': 'form-control selectpicker', 'data-live-search': 'true'}
                )
            )

        elif survey_field["type"] == "multiselect":
            fields[survey_field['variable']] = MultipleChoiceField(
                label=survey_field['question_name'],
                initial=survey_field['default'].split("\n"),
                required=survey_field['required'],
                help_text=survey_field['question_description'],
                choices=get_choices_as_tuples_list(survey_field["choices"], []),
                widget=SelectMultiple(
                    attrs={'class': 'form-control selectpicker', 'data-live-search': 'true'}
                )
            )

        elif survey_field["type"] == "integer":
            fields[survey_field['variable']] = IntegerField(
                label=survey_field['question_name'],
                initial=None if not survey_field['default'] else int(survey_field['default']),
                required=survey_field['required'],
                help_text=survey_field['question_description'],
                min_value=None if not survey_field['min'] else int(survey_field['min']),
                max_value=None if not survey_field['max'] else int(survey_field['max']),
                widget=NumberInput(
                    attrs={'class': 'form-control'}
                )
            )

        elif survey_field["type"] == "float":
            fields[survey_field['variable']] = FloatField(
                label=survey_field['question_name'],
                initial=None if not survey_field['default'] else float(survey_field['default']),
                required=survey_field['required'],
                help_text=survey_field['question_description'],
                min_value=None if not survey_field['min'] else float(survey_field['min']),
                max_value=None if not survey_field['max'] else float(survey_field['max']),
                widget=NumberInput(
                    attrs={'class': 'form-control', 'step': '0.1'}
                )
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
    if fields:
        fields[next(iter(fields))].separator = True
        fields[next(iter(fields))].form_title = form_title
    return fields


def prefill_form_with_user_values(fields: dict, fill_in_survey: dict, admin_fill_in_survey: dict):
    skipped_fields = ['squest_instance_name', 'billing_group_id']
    for field, value in fill_in_survey.items():
        if field not in skipped_fields:
            fields.get(field).initial = value
            fields.get(field).default = value
    for field, value in admin_fill_in_survey.items():
        if field not in skipped_fields:
            fields.get(field).initial = value
            fields.get(field).default = value
