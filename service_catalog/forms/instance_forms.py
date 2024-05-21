from django import forms

from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models import Instance
from service_catalog.models.instance import InstanceState


class InstanceForm(SquestModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(InstanceForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Instance
        fields = "__all__"


class InstanceFormRestricted(SquestModelForm):
    class Meta:
        model = Instance
        fields = ["name", "requester"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(InstanceFormRestricted, self).__init__(*args, **kwargs)
        if not self.user.has_perm('service_catalog.rename_instance', self.instance):
            self.fields.pop('name')
        if not self.user.has_perm('service_catalog.change_requester_on_instance', self.instance):
            self.fields.pop('requester')
        else:
            # Update the field to contains all user available in the scope
            self.fields["requester"].queryset = self.instance.quota_scope.users
