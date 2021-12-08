from django.contrib.contenttypes.models import ContentType
from django.forms import Form, MultipleChoiceField, SelectMultiple, ChoiceField, Select

from profiles.models import Team, TeamRoleBinding, UserRoleBinding


class TeamRoleForObjectForm(Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.object = kwargs.pop('object')
        super(TeamRoleForObjectForm, self).__init__(*args, **kwargs)
        self.fields['roles'].choices = [(role.id, role.name) for role in self.object.roles]
        self.fields['roles'].initial = self.object.roles.first().id
        teams = [Team.objects.get(id=binding.object_id) for binding in
                 UserRoleBinding.objects.filter(user=self.user,
                                                content_type=ContentType.objects.get_for_model(Team))]
        self.fields['teams'].choices = [(team.id, team.name) for team in teams]
        self.fields['teams'].initial = [binding.team.id for binding in
                                        TeamRoleBinding.objects.filter(
                                            role__id=self.fields["roles"].initial,
                                            object_id=self.object.id,
                                            content_type=ContentType.objects.get_for_model(self.object.__class__)
                                        )]

    roles = ChoiceField(label="Role",
                        required=False,
                        choices=[],
                        widget=Select(attrs={'class': 'selectpicker'})
                        )

    teams = MultipleChoiceField(label="Teams",
                                required=False,
                                choices=[],
                                widget=SelectMultiple(attrs={'class': 'selectpicker', 'data-live-search': "true"})
                                )
