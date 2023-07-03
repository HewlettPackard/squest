from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer, Serializer

from profiles.api.serializers import RBACSerializer
from profiles.models import Scope
from rest_framework.fields import MultipleChoiceField


class ScopeSerializer(ModelSerializer):
    rbac = RBACSerializer(many=True, read_only=True)

    class Meta:
        model = Scope
        fields = '__all__'
        read_only_fields = ('id',)


class ScopeCreateRBACSerializer(Serializer):
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
        self.scope = Scope.objects.get(id=kwargs.get('scope_id'))
        super(ScopeCreateRBACSerializer, self).__init__(*args, **kwargs)
        self.fields["users"].choices = self.scope.get_potential_users().values_list('id', 'username')
        self.fields["roles"].choices = Role.objects.all().values_list('id', 'name')

    def save(self):
        from profiles.models import Role
        for role_id in self.data.get('roles'):
            role = Role.objects.get(id=role_id)
            for user_id in self.data.get('users'):
                self.scope.add_user_in_role(User.objects.get(id=user_id), role)
