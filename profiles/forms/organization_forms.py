from django.forms import ModelMultipleChoiceField

from Squest.utils.squest_form import SquestForm
from profiles.models import Organization, Role, Team
from Squest.utils.squest_model_form import SquestModelForm


class OrganizationForm(SquestModelForm):
    class Meta:
        model = Organization
        fields = ["name"]
