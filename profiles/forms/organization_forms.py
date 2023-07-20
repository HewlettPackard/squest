from Squest.utils.squest_model_form import SquestModelForm
from profiles.models import Organization


class OrganizationForm(SquestModelForm):
    class Meta:
        model = Organization
        fields = ["name", "description", "roles"]
