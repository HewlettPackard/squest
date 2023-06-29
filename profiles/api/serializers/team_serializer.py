from profiles.api.serializers import ScopeSerializer
from profiles.models import Team, Organization


class TeamSerializer(ScopeSerializer):
    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ('id',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        view = self.context.get('view')
        self.organization_id = None
        if view:
            self.organization_id = view.kwargs.get('organization_id', None)
            # Change the queryset when the organization is present in url kwargs
            if self.organization_id:
                self.fields.fields['org'].queryset = Organization.objects.filter(id=self.organization_id)
                self.fields.fields['org'].required = False
                self.fields.fields['org'].initial = self.organization_id
        else:
            self.fields.fields.pop('org')

    def is_valid(self, *args, **kwargs):
        # Override the organization when it is present in url kwargs
        if self.organization_id:
            self.initial_data['org'] = self.organization_id
        return super().is_valid(*args, **kwargs)
