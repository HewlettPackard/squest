from django import forms


def _get_field_group(field_name, enable_fields):
    if enable_fields[field_name]:
        return "User"
    return "Admin"


def get_choices_from_string(string_with_anti_slash_n):
    split_lines = string_with_anti_slash_n.splitlines()
    returned_list = list()
    for line in split_lines:
        returned_list.append((line, line))
    return returned_list


def get_fields_from_survey(survey, enable_fields=None):
    fields = {}
    for survey_filed in survey["spec"]:
        if survey_filed["type"] == "text":
            fields[survey_filed['variable']] = forms. \
                CharField(label=survey_filed['question_name'],
                          initial=survey_filed['default'],
                          required=survey_filed['required'],
                          help_text=survey_filed['question_description'],
                          min_length=survey_filed['min'],
                          max_length=survey_filed['max'],
                          widget=forms.TextInput(attrs={'class': 'form-control'}))

        elif survey_filed["type"] == "textarea":
            fields[survey_filed['variable']] = forms. \
                CharField(label=survey_filed['question_name'],
                          initial=survey_filed['default'],
                          required=survey_filed['required'],
                          help_text=survey_filed['question_description'],
                          min_length=survey_filed['min'],
                          max_length=survey_filed['max'],
                          widget=forms.Textarea(attrs={'class': 'form-control'}))

        elif survey_filed["type"] == "password":
            fields[survey_filed['variable']] = forms. \
                CharField(label=survey_filed['question_name'],
                          required=survey_filed['required'],
                          help_text=survey_filed['question_description'],
                          min_length=survey_filed['min'],
                          max_length=survey_filed['max'],
                          widget=forms.PasswordInput(render_value=True, attrs={'class': 'form-control'}))

        elif survey_filed["type"] == "multiplechoice":
            fields[survey_filed['variable']] = forms. \
                ChoiceField(label=survey_filed['question_name'],
                            initial=survey_filed['default'],
                            required=survey_filed['required'],
                            help_text=survey_filed['question_description'],
                            choices=get_choices_from_string(survey_filed["choices"]),
                            error_messages={'required': 'At least you must select one choice'},
                            widget=forms.Select(attrs={'class': 'form-control'}))

        elif survey_filed["type"] == "multiselect":
            fields[survey_filed['variable']] = forms. \
                MultipleChoiceField(label=survey_filed['question_name'],
                                    initial=survey_filed['default'].split("\n"),
                                    required=survey_filed['required'],
                                    help_text=survey_filed['question_description'],
                                    choices=get_choices_from_string(survey_filed["choices"]),
                                    widget=forms.SelectMultiple(
                                        attrs={'class': 'form-control', 'choices': 'OPTIONS_TUPPLE'}))

        elif survey_filed["type"] == "integer":
            fields[survey_filed['variable']] = forms. \
                IntegerField(label=survey_filed['question_name'],
                             initial=int(survey_filed['default']),
                             required=survey_filed['required'],
                             help_text=survey_filed['question_description'],
                             min_value=survey_filed['min'],
                             max_value=survey_filed['max'],
                             widget=forms.NumberInput(attrs={'class': 'form-control'}))

        elif survey_filed["type"] == "float":
            fields[survey_filed['variable']] = forms. \
                FloatField(label=survey_filed['question_name'],
                           initial=float(survey_filed['default']),
                           required=survey_filed['required'],
                           help_text=survey_filed['question_description'],
                           min_value=survey_filed['min'],
                           max_value=survey_filed['max'],
                           widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}))
        if enable_fields:
            fields[survey_filed['variable']].group = _get_field_group(field_name=survey_filed['variable'],
                                                                      enable_fields=enable_fields)
    return fields


def prefill_form_with_user_values(fields: dict, fill_in_survey: dict):
    skipping_fields = ['instance_name', 'billing_group_id']
    for field, value in fill_in_survey.items():
        if field not in skipping_fields:
            fields.get(field).initial = value
