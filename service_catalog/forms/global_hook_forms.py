from django import forms
from django.core.exceptions import ValidationError
from django.forms import ChoiceField

from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models import GlobalHook
from service_catalog.models.instance import InstanceState
from service_catalog.models.request import RequestState


class GlobalHookForm(SquestModelForm):
    def __init__(self, *args, **kwargs):
        super(GlobalHookForm, self).__init__(*args, **kwargs)
        self.fields['operation'].widget.attrs['class'] = 'form-control'
        self.fields['state'] = ChoiceField(label="State",
                                           choices=InstanceState.choices + RequestState.choices,
                                           error_messages={'required': 'At least you must select one state'},
                                           widget=forms.Select(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super(GlobalHookForm, self).clean()
        model = cleaned_data.get('model')
        state = cleaned_data.get('state')

        choices = ""
        if model == "Request":
            choices = RequestState.choices
        if model == "Instance":
            choices = InstanceState.choices
        if state not in (choice[0] for choice in choices):
            raise ValidationError({
                'state': f"'{state}' is not a valid state of model '{model}'"
            })
        return cleaned_data

    class Meta:
        model = GlobalHook
        fields = ["name", "model", "service", "operation", "state", "job_template", "extra_vars"]
