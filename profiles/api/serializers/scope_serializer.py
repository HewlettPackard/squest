from django.contrib.auth.models import User
from rest_framework.fields import MultipleChoiceField, SerializerMethodField
from rest_framework.serializers import ModelSerializer

from profiles.api.serializers import RBACSerializer
from profiles.models import AbstractScope, Scope


class AbstractScopeSerializer(ModelSerializer):
    rbac = RBACSerializer(many=True, read_only=True)

    class Meta:
        model = AbstractScope
        fields = '__all__'


class ScopeSerializerManager(ModelSerializer):
    organization = SerializerMethodField()
    team = SerializerMethodField()

    class Meta:
        model = Scope
        fields = '__all__'

    def get_organization(self, obj):
        if obj.is_org:
            return {"id": obj.id, "name": obj.name}
        elif obj.is_team:
            team = obj.get_object()
            return {"id": team.org.id, "name": team.org.name}
        else:
            return {}

    def get_team(self, obj):
        if obj.is_org:
            return {}
        elif obj.is_team:
            return {"id": obj.id, "name": obj.name}
        else:
            return {}


class ScopeSerializerNested(ScopeSerializerManager):
    pass


class ScopeSerializer(AbstractScopeSerializer, ScopeSerializerManager):
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
