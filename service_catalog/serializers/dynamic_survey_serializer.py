from rest_framework.serializers import Serializer, ChoiceField, CharField, MultipleChoiceField, IntegerField, FloatField

from service_catalog.forms.utils import get_choices_from_string


class DynamicSurveySerializer(Serializer):
    def __init__(self, *args, **kwargs):
        self.survey = kwargs.pop('fill_in_survey')
        super(DynamicSurveySerializer, self).__init__(*args, **kwargs)
        self.fields.update(self._get_fields_from_survey())

    def _get_fields_from_survey(self):
        fields = {}
        for survey_filed in self.survey["spec"]:
            if survey_filed["type"] == "text":
                fields[survey_filed['variable']] = CharField(
                    label=survey_filed['question_name'],
                    initial=survey_filed['default'],
                    required=survey_filed['required'],
                    help_text=survey_filed['question_description'],
                    min_length=survey_filed['min'],
                    max_length=survey_filed['max']
                )

            elif survey_filed["type"] == "textarea":
                fields[survey_filed['variable']] = CharField(
                    label=survey_filed['question_name'],
                    initial=survey_filed['default'],
                    required=survey_filed['required'],
                    help_text=survey_filed['question_description'],
                    min_length=survey_filed['min'],
                    max_length=survey_filed['max']
                )

            elif survey_filed["type"] == "password":
                fields[survey_filed['variable']] = CharField(
                    label=survey_filed['question_name'],
                    required=survey_filed['required'],
                    help_text=survey_filed['question_description'],
                    min_length=survey_filed['min'],
                    max_length=survey_filed['max'],
                )

            elif survey_filed["type"] == "multiplechoice":
                fields[survey_filed['variable']] = ChoiceField(
                    label=survey_filed['question_name'],
                    initial=survey_filed['default'],
                    required=survey_filed['required'],
                    help_text=survey_filed['question_description'],
                    choices=get_choices_from_string(survey_filed["choices"]),
                    error_messages={'required': 'At least you must select one choice'}
                )

            elif survey_filed["type"] == "multiselect":
                fields[survey_filed['variable']] = MultipleChoiceField(
                    label=survey_filed['question_name'],
                    initial=survey_filed['default'].split("\n"),
                    required=survey_filed['required'],
                    help_text=survey_filed['question_description'],
                    choices=get_choices_from_string(survey_filed["choices"]),
                )

            elif survey_filed["type"] == "integer":
                fields[survey_filed['variable']] = IntegerField(
                    label=survey_filed['question_name'],
                    initial=int(survey_filed['default']),
                    required=survey_filed['required'],
                    help_text=survey_filed['question_description'],
                    min_value=survey_filed['min'],
                    max_value=survey_filed['max'],
                )

            elif survey_filed["type"] == "float":
                fields[survey_filed['variable']] = FloatField(
                    label=survey_filed['question_name'],
                    initial=float(survey_filed['default']),
                    required=survey_filed['required'],
                    help_text=survey_filed['question_description'],
                    min_value=survey_filed['min'],
                    max_value=survey_filed['max'],
                )
        return fields

