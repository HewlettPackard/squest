from django import forms

from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models import Instance
from service_catalog.models.instance import InstanceState


class InstanceForm(SquestModelForm):
    class Meta:
        model = Instance
        fields = "__all__"
