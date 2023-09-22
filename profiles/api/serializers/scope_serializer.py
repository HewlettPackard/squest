from django.contrib.auth.models import User
from rest_framework.fields import MultipleChoiceField
from rest_framework.serializers import ModelSerializer, Serializer

from profiles.api.serializers import RBACSerializer
from profiles.models import AbstractScope, Scope


class AbstractScopeSerializer(ModelSerializer):
    rbac = RBACSerializer(many=True, read_only=True)

    class Meta:
        model = AbstractScope
        fields = '__all__'


class ScopeSerializer(AbstractScopeSerializer):
    class Meta:
        model = Scope
        fields = '__all__'


class AbstractScopeCreateRBACSerializer(Serializer):
    roles = MultipleChoiceField(
        choices=[],
        required=True,
    )
    users = MultipleChoiceField(
        choices=[],
        required=True,
    )

    def __init__(self, *args, **kwargs):
        from profiles.models import Role
        self.scope = AbstractScope.objects.get(id=kwargs.pop('scope_id'))
        super(AbstractScopeCreateRBACSerializer, self).__init__(*args, **kwargs)
        self.fields["users"].choices = self.scope.get_potential_users().values_list('id', 'username')
        self.fields["roles"].choices = Role.objects.values_list('id', 'name')

    def save(self):
        from profiles.models import Role
        for role_id in self.data.get('roles'):
            role = Role.objects.get(id=role_id)
            for user_id in self.data.get('users'):
                self.scope.add_user_in_role(User.objects.get(id=user_id), role)
