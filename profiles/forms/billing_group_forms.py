from profiles.models import BillingGroup
from Squest.utils.squest_model_form import SquestModelForm

class BillingGroupForm(SquestModelForm):
    class Meta:
        model = BillingGroup
        fields = ["name"]
