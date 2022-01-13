from Squest.utils.squest_model_form import SquestModelForm
from profiles.models import Quota


class QuotaForm(SquestModelForm):
    class Meta:
        model = Quota
        fields = ["name", "attribute_definitions"]
