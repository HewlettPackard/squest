from profiles.models import Organization
from profiles.models.team import Team
from Squest.utils.squest_model_form import SquestModelForm


class TeamForm(SquestModelForm):
    class Meta:
        model = Team
        fields = ["name", "org"]


class OrganizationTeamForm(SquestModelForm):
    class Meta:
        model = Team
        fields = ["name", "org"]

    def __init__(self, *args, **kwargs):
        self.org_id = kwargs.pop('org_id')
        super(OrganizationTeamForm, self).__init__(*args, **kwargs)
        org_qs = Organization.objects.filter(id=self.org_id)
        self.fields['org'].queryset = org_qs
        self.fields['org'].initial = org_qs.first()
        self.fields['org'].disabled = True
