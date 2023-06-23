from django.contrib.auth.models import User
from django.forms import ModelMultipleChoiceField

from Squest.utils.squest_form import SquestForm
from profiles.models import Role


class ScopeCreateRBACForm(SquestForm):
    roles = ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        required=True,
    )
    users = ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.scope = kwargs.pop('scope')
        super(ScopeCreateRBACForm, self).__init__(*args, **kwargs)
        self.fields["users"].queryset = self.scope.get_perspective_users()

    def save(self):
        for role in self.cleaned_data.get('roles'):
            group = self.scope.get_group_role(role.name)
            for user in self.cleaned_data.get('users'):
                self.scope.add_user_in_role(user, role.name)
