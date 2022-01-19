from profiles.models.team import Team
from Squest.utils.squest_model_form import SquestModelForm


class TeamForm(SquestModelForm):
    class Meta:
        model = Team
        fields = ["name"]
