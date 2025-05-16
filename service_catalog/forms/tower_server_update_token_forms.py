from django import forms

from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models import TowerServer


class TowerServerUpdateTokenForm(SquestModelForm):
    token = forms.CharField(label="Token",
                            widget=forms.TextInput(),
    )

    def __init__(self, *args, **kwargs):
        super(TowerServerUpdateTokenForm, self).__init__(*args, **kwargs)
        self.initial['token'] = ""


    class Meta:
        model = TowerServer
        fields = ["token"]
