from profiles.models import Organization
from Squest.utils.squest_model_form import SquestModelForm


class OrganizationForm(SquestModelForm):
    class Meta:
        model = Organization
        fields = ["name", "description", "roles"]
