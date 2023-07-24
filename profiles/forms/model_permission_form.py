from django.contrib.auth.models import Permission

from Squest.utils.squest_model_form import SquestModelForm


class ModelPermissionForm(SquestModelForm):
    class Meta:
        model = Permission
        exclude = ['content_type']

    def __init__(self, content_type, *args, **kwargs):
        # get arguments from instance
        self.permission_content_type = content_type
        super().__init__(*args, **kwargs)
        self.fields['name'].help_text = f'A short description of the permission.'
        self.fields['codename'].help_text = f'Should be split by "_" and finished by object type ("{self.permission_content_type.model}").'

    def save(self, commit=True):
        permission = super().save(False)
        permission.content_type = self.permission_content_type
        return permission
