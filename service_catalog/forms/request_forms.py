from service_catalog.models import Request
from Squest.utils.squest_model_form import SquestModelForm


class RequestForm(SquestModelForm):
    class Meta:
        model = Request
        fields = "__all__"
