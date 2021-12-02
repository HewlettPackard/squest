from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.forms import Form, MultipleChoiceField, SelectMultiple, ChoiceField, Select

from profiles.models import UserRoleBinding, Team


class UserRoleForObjectForm(Form):
    def __init__(self, *args, **kwargs):
        self.object = kwargs.pop('object')
        super(UserRoleForObjectForm, self).__init__(*args, **kwargs)
        self.fields['roles'].choices = [(role.id, role.name) for role in self.object.roles]
        self.fields['roles'].initial = self.object.roles.first().id
        self.fields['users'].choices = [(user.id, user.username) for user in User.objects.all()]
        self.fields['users'].initial = [binding.user.id for binding in
                                        UserRoleBinding.objects.filter(
                                            role__id=self.fields["roles"].initial,
                                            object_id=self.object.id,
                                            content_type=ContentType.objects.get_for_model(self.object.__class__)
                                        )]

    roles = ChoiceField(label="Role",
                        required=False,
                        choices=[],
                        widget=Select(attrs={'class': 'selectpicker'})
                        )

    users = MultipleChoiceField(label="Users",
                                required=False,
                                choices=[],
                                widget=SelectMultiple(attrs={'class': 'selectpicker', 'data-live-search': "true"})
                                )
