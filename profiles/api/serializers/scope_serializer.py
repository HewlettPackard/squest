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


class AbstractScopeCreateRBACSerializer(ModelSerializer):
    roles = MultipleChoiceField(
        choices=[],
        required=True,
        write_only=True
    )
    users = MultipleChoiceField(
        choices=[],
        required=True,
        write_only=True
    )
    rbac = RBACSerializer(many=True, read_only=True)

    class Meta:
        model = AbstractScope
        fields = ('id', 'rbac', 'name', 'roles', 'users')
        read_only_fields = ('id', 'rbac', 'name')

    def __init__(self, *args, **kwargs):
        from profiles.models import Role
        super(AbstractScopeCreateRBACSerializer, self).__init__(*args, **kwargs)
        if self.instance is None:
            self.fields["users"].choices = User.objects.none().values_list('id', 'username')
        else:
            self.fields["users"].choices = self.instance.get_potential_users().values_list('id', 'username')
        self.fields["roles"].choices = Role.objects.values_list('id', 'name')

    def save(self):
        from profiles.models import Role
        for role_id in self.validated_data.get('roles'):
            role = Role.objects.get(id=role_id)
            for user_id in self.validated_data.get('users'):
                self.instance.add_user_in_role(User.objects.get(id=user_id), role)
        return self.instance
