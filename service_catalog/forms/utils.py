from django import forms


def get_choices_from_string(string_with_anti_slash_n):
    split_lines = string_with_anti_slash_n.splitlines()
    returned_list = list()
    for line in split_lines:
        returned_list.append((line, line))
    return returned_list


def get_fields_from_survey(survey):
    fields = {}
    for survey_filed in survey["spec"]:
        if survey_filed["type"] == "text":
            fields[survey_filed['variable']] = forms. \
                CharField(label=survey_filed['question_name'],
                          initial=survey_filed['default'],
                          required=survey_filed['required'],
                          min_length=survey_filed['min'],
                          max_length=survey_filed['max'],
                          widget=forms.TextInput(attrs={'class': 'form-control'}))

        elif survey_filed["type"] == "textarea":
            fields[survey_filed['variable']] = forms. \
                CharField(label=survey_filed['question_name'],
                          initial=survey_filed['default'],
                          required=survey_filed['required'],
                          min_length=survey_filed['min'],
                          max_length=survey_filed['max'],
                          widget=forms.Textarea(attrs={'class': 'form-control'}))

        elif survey_filed["type"] == "password":
            fields[survey_filed['variable']] = forms. \
                CharField(label=survey_filed['question_name'],
                          required=survey_filed['required'],
                          min_length=survey_filed['min'],
                          max_length=survey_filed['max'],
                          widget=forms.PasswordInput(attrs={'class': 'form-control'}))

        elif survey_filed["type"] == "multiplechoice":
            fields[survey_filed['variable']] = forms. \
                ChoiceField(label=survey_filed['question_name'],
                            initial=survey_filed['default'],
                            required=survey_filed['required'],
                            choices=get_choices_from_string(survey_filed["choices"]),
                            error_messages={'required': 'At least you must select one choice'},
                            widget=forms.Select(attrs={'class': 'form-control'}))

        elif survey_filed["type"] == "multiselect":
            fields[survey_filed['variable']] = forms. \
                MultipleChoiceField(label=survey_filed['question_name'],
                                    initial=survey_filed['default'].split("\n"),
                                    required=survey_filed['required'],
                                    choices=get_choices_from_string(survey_filed["choices"]),
                                    widget=forms.SelectMultiple(
                                        attrs={'class': 'form-control', 'choices': 'OPTIONS_TUPPLE'}))

        elif survey_filed["type"] == "integer":
            fields[survey_filed['variable']] = forms. \
                IntegerField(label=survey_filed['question_name'],
                             initial=survey_filed['default'],
                             required=survey_filed['required'],
                             min_value=survey_filed['min'],
                             max_value=survey_filed['max'],
                             widget=forms.NumberInput(attrs={'class': 'form-control'}))

        elif survey_filed["type"] == "float":
            fields[survey_filed['variable']] = forms. \
                FloatField(label=survey_filed['question_name'],
                           initial=survey_filed['default'],
                           required=survey_filed['required'],
                           min_value=survey_filed['min'],
                           max_value=survey_filed['max'],
                           widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}))
    return fields
