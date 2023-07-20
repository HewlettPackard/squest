from Squest.utils.squest_model_form import SquestModelForm
from profiles.models import Role


class RoleForm(SquestModelForm):
    class Meta:
        model = Role
        fields = '__all__'
