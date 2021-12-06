from django.contrib.contenttypes.models import ContentType
from django.forms import Form, MultipleChoiceField, SelectMultiple, ChoiceField, Select

from profiles.models import Team, TeamRoleBinding


class TeamRoleForObjectForm(Form):
    def __init__(self, *args, **kwargs):
        self.object = kwargs.pop('object')
        super(TeamRoleForObjectForm, self).__init__(*args, **kwargs)
        self.fields['roles'].choices = [(role.id, role.name) for role in self.object.roles]
        self.fields['roles'].initial = self.object.roles.first().id
        self.fields['teams'].choices = [(team.id, team.name) for team in Team.objects.all()]
        self.fields['teams'].initial = [binding.user.id for binding in
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
