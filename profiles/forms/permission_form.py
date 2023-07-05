from django.contrib.auth.models import Permission

from Squest.utils.squest_model_form import SquestModelForm


class PermissionForm(SquestModelForm):
    class Meta:
        model = Permission
        fields = "__all__"
