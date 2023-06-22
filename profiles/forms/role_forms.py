from profiles.models import Role
from Squest.utils.squest_model_form import SquestModelForm


class RoleForm(SquestModelForm):
    class Meta:
        model = Role
        fields = '__all__'
