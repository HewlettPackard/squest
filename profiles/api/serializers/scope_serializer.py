from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer, Serializer
from profiles.models import Scope, Role
from rest_framework.fields import MultipleChoiceField


class ScopeSerializer(ModelSerializer):
    class Meta:
        model = Scope
        fields = '__all__'
        read_only_fields = ('id',)


class ScopeCreateRBACSerializer(Serializer):
    roles = MultipleChoiceField(
        choices=Role.objects.all().values_list('id', 'name'),
        required=True,
    )
    users = MultipleChoiceField(
        choices=User.objects.none(),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.scope = Scope.objects.get(id=kwargs.get('context').get('view').kwargs.get('scope_id'))
        super(ScopeCreateRBACSerializer, self).__init__(*args, **kwargs)
        self.fields["users"].choices = self.scope.get_perspective_users().values_list('id', 'username')

    def save(self):
        for role_id in self.data.get('roles'):
            role = Role.objects.get(id=role_id)
            for user_id in self.data.get('users'):
                self.scope.add_user_in_role(User.objects.get(id=user_id), role.name)
