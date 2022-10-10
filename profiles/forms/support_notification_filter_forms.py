from django.core.exceptions import ValidationError
from django.forms import MultipleChoiceField, SelectMultiple, HiddenInput

from Squest.utils.squest_model_form import SquestModelForm
from profiles.models import InstanceNotification
from service_catalog.models import InstanceState


class SupportNotificationFilterForm(SquestModelForm):
    instance_states = MultipleChoiceField(label="Instance states",
                                          required=False,
                                          choices=InstanceState.choices,
                                          widget=SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, user, *args, **kwargs):
        # get arguments from instance
        self.user = user
        super(SupportNotificationFilterForm, self).__init__(*args, **kwargs)
        self.fields['profile'].widget = HiddenInput()
        self.fields['profile'].initial = self.user.profile.id
        self.fields['profile'].choices = [(self.user.profile.id, self.user.username)]

    def clean_profile(self):
        cleaned_profile = self.cleaned_data['profile']
        if cleaned_profile.id != self.user.profile.id:
            raise ValidationError("Notification filters cannot be created for other users")
        return cleaned_profile

    class Meta:
        model = InstanceNotification
        fields = ["name", "services", "instance_states", "when", "profile"]
