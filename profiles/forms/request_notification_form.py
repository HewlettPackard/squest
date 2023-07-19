from django.forms import MultipleChoiceField, SelectMultiple

from Squest.utils.squest_model_form import SquestModelForm
from profiles.models.request_notification import RequestNotification
from service_catalog.models import RequestState


class RequestNotificationForm(SquestModelForm):
    class Meta:
        model = RequestNotification
        fields = ["name", "services", "operations", "request_states", "when"]

    request_states = MultipleChoiceField(label="Request states",
                                         required=False,
                                         choices=RequestState.choices,
                                         widget=SelectMultiple(attrs={'class': 'form-control'}))

    def __init__(self, user, *args, **kwargs):
        # get arguments from instance
        self.user = user
        super(RequestNotificationForm, self).__init__(*args, **kwargs)


    def save(self, commit=True):
        obj = super().save(False)
        obj.profile = self.user.profile
        obj.save()
        return obj
