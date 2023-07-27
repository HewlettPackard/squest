from django.contrib.auth.models import Permission

from Squest.utils.squest_model_form import SquestModelForm


class PermissionForm(SquestModelForm):
    class Meta:
        model = Permission
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].help_text = f'A short description of the permission.'
        self.fields['codename'].help_text = f'Should be split by "_" and finished by the object type (depends on ' \
                                            f'content type chosen).'
