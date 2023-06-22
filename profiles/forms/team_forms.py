from profiles.models import Organization
from profiles.models.team import Team
from Squest.utils.squest_model_form import SquestModelForm


class TeamForm(SquestModelForm):
    class Meta:
        model = Team
        fields = ["org", "name", "description", "roles"]

    def __init__(self, *args, **kwargs):
        self.organization_id = kwargs.pop('organization_id', None)
        super().__init__(*args, **kwargs)
        # # Change the queryset when the organization is present in url kwargs
        if self.organization_id:
            self.fields['org'].queryset = Organization.objects.filter(id=self.organization_id)
            self.fields['org'].initial = self.organization_id
            self.fields['org'].disabled = True
