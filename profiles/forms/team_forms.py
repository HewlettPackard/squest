from Squest.utils.squest_model_form import SquestModelForm
from profiles.models.team import Team


class TeamForm(SquestModelForm):
    class Meta:
        model = Team
        fields = ["org", "name", "description", "roles"]
