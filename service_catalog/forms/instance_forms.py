import urllib3
from django import forms
from service_catalog.models import Instance
from service_catalog.models.instance import InstanceState
from Squest.utils.squest_model_form import SquestModelForm
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class InstanceForm(SquestModelForm):
    state = forms.ChoiceField(
        choices=InstanceState.choices,
        required=True,
        widget=forms.Select())

    class Meta:
        model = Instance
        fields = "__all__"
