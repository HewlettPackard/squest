from Squest.utils.squest_model_form import SquestModelForm
from profiles.models import QuotaBinding


class QuotaBindingForm(SquestModelForm):
    class Meta:
        model = QuotaBinding
        fields = ["limit"]
