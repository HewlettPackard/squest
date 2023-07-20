from Squest.utils.squest_model_form import SquestModelForm
from profiles.models import GlobalPermission


class GlobalPermissionForm(SquestModelForm):
    class Meta:
        model = GlobalPermission
        fields = ["user_permissions"]
