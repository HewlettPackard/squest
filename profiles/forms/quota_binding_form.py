from Squest.utils.squest_model_form import SquestModelForm
from profiles.models import QuotaBinding


class QuotaBindingForm(SquestModelForm):
    class Meta:
        model = QuotaBinding
        fields = ["limit", "yellow_threshold_percent", "red_threshold_percent"]
