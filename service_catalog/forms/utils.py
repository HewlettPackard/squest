from django import forms


def _get_field_group(field_name, enable_fields):
    if enable_fields[field_name]:
        return "1. User"
    return "2. Admin"


def get_choices_from_string(string_with_anti_slash_n):
    split_lines = string_with_anti_slash_n.splitlines()
    returned_list = [('', "Select an option")]
    for line in split_lines:
        returned_list.append((line, line))
    return returned_list


def get_fields_from_survey(survey, enable_fields=None):
    fields = {}
    for survey_field in survey["spec"]:
        if survey_field["type"] == "text":
            fields[survey_field['variable']] = forms. \
                CharField(label=survey_field['question_name'],
                          initial=survey_field['default'],
                          required=survey_field['required'],
                          help_text=survey_field['question_description'],
                          min_length=survey_field['min'],
                          max_length=survey_field['max'],
                          widget=forms.TextInput(attrs={'class': 'form-control'}))

        elif survey_field["type"] == "textarea":
            fields[survey_field['variable']] = forms. \
                CharField(label=survey_field['question_name'],
                          initial=survey_field['default'],
                          required=survey_field['required'],
                          help_text=survey_field['question_description'],
                          min_length=survey_field['min'],
                          max_length=survey_field['max'],
                          widget=forms.Textarea(attrs={'class': 'form-control'}))

        elif survey_field["type"] == "password":
            fields[survey_field['variable']] = forms. \
                CharField(label=survey_field['question_name'],
                          required=survey_field['required'],
                          help_text=survey_field['question_description'],
                          min_length=survey_field['min'],
                          max_length=survey_field['max'],
                          widget=forms.PasswordInput(render_value=True, attrs={'class': 'form-control'}))

        elif survey_field["type"] == "multiplechoice":
            fields[survey_field['variable']] = forms. \
                ChoiceField(label=survey_field['question_name'],
                            initial=survey_field['default'],
                            required=survey_field['required'],
                            help_text=survey_field['question_description'],
                            choices=get_choices_from_string(survey_field["choices"]),
                            error_messages={'required': 'At least you must select one choice'},
                            widget=forms.Select(attrs={'class': 'form-control'}))

        elif survey_field["type"] == "multiselect":
            fields[survey_field['variable']] = forms. \
                MultipleChoiceField(label=survey_field['question_name'],
                                    initial=survey_field['default'].split("\n"),
                                    required=survey_field['required'],
                                    help_text=survey_field['question_description'],
                                    choices=get_choices_from_string(survey_field["choices"]),
                                    widget=forms.SelectMultiple(
                                        attrs={'class': 'form-control', 'choices': 'OPTIONS_TUPPLE'}))

        elif survey_field["type"] == "integer":
            fields[survey_field['variable']] = forms. \
                IntegerField(label=survey_field['question_name'],
                             initial=None if not survey_field['default'] else int(survey_field['default']),
                             required=survey_field['required'],
                             help_text=survey_field['question_description'],
                             min_value=None if not survey_field['min'] else int(survey_field['min']),
                             max_value=None if not survey_field['max'] else int(survey_field['max']),
                             widget=forms.NumberInput(attrs={'class': 'form-control'}))

        elif survey_field["type"] == "float":
            fields[survey_field['variable']] = forms. \
                FloatField(label=survey_field['question_name'],
                           initial=None if not survey_field['default'] else float(survey_field['default']),
                           required=survey_field['required'],
                           help_text=survey_field['question_description'],
                           min_value=None if not survey_field['min'] else float(survey_field['min']),
                           max_value=None if not survey_field['max'] else float(survey_field['max']),
                           widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}))
        if enable_fields:
            fields[survey_field['variable']].group = _get_field_group(field_name=survey_field['variable'],
                                                                      enable_fields=enable_fields)
    if fields:
        fields[next(iter(fields))].separator = True
        fields[next(iter(fields))].form_title = "2. Service fields"
    return fields


def prefill_form_with_user_values(fields: dict, fill_in_survey: dict):
    skipping_fields = ['instance_name', 'billing_group_id']
    for field, value in fill_in_survey.items():
        if field not in skipping_fields:
            fields.get(field).initial = value
