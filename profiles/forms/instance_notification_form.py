from django.forms import MultipleChoiceField, SelectMultiple

from Squest.utils.squest_model_form import SquestModelForm
from profiles.models import InstanceNotification
from service_catalog.models import InstanceState


class InstanceNotificationForm(SquestModelForm):
    class Meta:
        model = InstanceNotification
        fields = ["name", "services", "instance_states", "when"]

    instance_states = MultipleChoiceField(label="Instance states",
                                          required=False,
                                          choices=InstanceState.choices,
                                          widget=SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, user, *args, **kwargs):
        # get arguments from instance
        self.user = user
        super(InstanceNotificationForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super().save(False)
        obj.profile = self.user.profile
        obj.save()
        return obj
