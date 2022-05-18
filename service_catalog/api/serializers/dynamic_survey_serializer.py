import logging

from rest_framework.serializers import Serializer, ChoiceField, CharField, MultipleChoiceField, IntegerField, FloatField

from service_catalog.forms.utils import get_choices_from_string
from Squest.utils.plugin_controller import PluginController


logger = logging.getLogger(__name__)


class DynamicSurveySerializer(Serializer):
    def __init__(self, *args, **kwargs):
        self.survey = kwargs.pop('fill_in_survey')
        self.read_only_form = kwargs.pop('read_only_form', False)
        super(DynamicSurveySerializer, self).__init__(*args, **kwargs)
        self.fields.update(self._get_fields_from_survey())

    def _set_initial_and_default(self, fill_in_survey: dict):
        for field, value in fill_in_survey.items():
            self.fields.get(field).initial = value
            self.fields.get(field).default = value

    def _get_fields_from_survey(self):
        fields = {}
        for survey_field in self.survey["spec"]:
            if survey_field["type"] == "text":
                fields[survey_field['variable']] = CharField(
                    label=survey_field['question_name'],
                    initial=survey_field['default'],
                    required=False if self.read_only_form else survey_field['required'],
                    help_text=survey_field['question_description'],
                    min_length=survey_field['min'],
                    max_length=survey_field['max']
                )

            elif survey_field["type"] == "textarea":
                fields[survey_field['variable']] = CharField(
                    label=survey_field['question_name'],
                    initial=survey_field['default'],
                    required=False if self.read_only_form else survey_field['required'],
                    help_text=survey_field['question_description'],
                    min_length=survey_field['min'],
                    max_length=survey_field['max']
                )

            elif survey_field["type"] == "password":
                fields[survey_field['variable']] = CharField(
                    label=survey_field['question_name'],
                    required=False if self.read_only_form else survey_field['required'],
                    help_text=survey_field['question_description'],
                    min_length=survey_field['min'],
                    max_length=survey_field['max'],
                )

            elif survey_field["type"] == "multiplechoice":
                fields[survey_field['variable']] = ChoiceField(
                    label=survey_field['question_name'],
                    initial=survey_field['default'],
                    required=False if self.read_only_form else survey_field['required'],
                    help_text=survey_field['question_description'],
                    choices=get_choices_from_string(survey_field["choices"]),
                    error_messages={'required': 'At least you must select one choice'}
                )

            elif survey_field["type"] == "multiselect":
                fields[survey_field['variable']] = MultipleChoiceField(
                    label=survey_field['question_name'],
                    initial=survey_field['default'].split("\n"),
                    required=False if self.read_only_form else survey_field['required'],
                    help_text=survey_field['question_description'],
                    choices=get_choices_from_string(survey_field["choices"]),
                )

            elif survey_field["type"] == "integer":
                fields[survey_field['variable']] = IntegerField(
                    label=survey_field['question_name'],
                    initial=0 if not survey_field['default'] else int(survey_field['default']),
                    required=False if self.read_only_form else survey_field['required'],
                    help_text=survey_field['question_description'],
                    min_value=survey_field['min'],
                    max_value=survey_field['max'],
                )

            elif survey_field["type"] == "float":
                fields[survey_field['variable']] = FloatField(
                    label=survey_field['question_name'],
                    initial=0 if not survey_field['default'] else float(survey_field['default']),
                    required=False if self.read_only_form else survey_field['required'],
                    help_text=survey_field['question_description'],
                    min_value=survey_field['min'],
                    max_value=survey_field['max'],
                )

            if survey_field["validators"] is not None and len(survey_field["validators"]) > 0:
                list_validator_def = list()
                for validator_file in survey_field["validators"]:
                    # load dynamically the user provided validator
                    loaded_class_plugin = PluginController.get_api_field_validator_def(validator_file)
                    if loaded_class_plugin is not None:
                        list_validator_def.append(loaded_class_plugin)
                        logger.info(f"[Form utils] User validator plugin loaded: {validator_file}")
                fields[survey_field['variable']].validators = list_validator_def

            if self.read_only_form:
                fields[survey_field['variable']].default = survey_field['default']

        return fields
