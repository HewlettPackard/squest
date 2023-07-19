from profiles.models import GlobalPermission
from Squest.utils.squest_model_form import SquestModelForm


class GlobalPermissionForm(SquestModelForm):
    class Meta:
        model = GlobalPermission
        fields = ["user_permissions"]
