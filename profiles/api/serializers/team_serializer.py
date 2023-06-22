from rest_framework.serializers import ModelSerializer

from profiles.models import Team, Organization


class TeamSerializer(ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ('id',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization_id = self.context.get('view').kwargs.get('organization_id', None)
        # Change the queryset when the organization is present in url kwargs
        if self.organization_id:
            self.fields.fields['org'].queryset = Organization.objects.filter(id=self.organization_id)
            self.fields.fields['org'].required = False
            self.fields.fields['org'].initial = self.organization_id

    def is_valid(self, *args, **kwargs):
        # Override the organization when it is present in url kwargs
        if self.organization_id:
            self.initial_data['org'] = self.organization_id
        return super().is_valid(*args, **kwargs)
