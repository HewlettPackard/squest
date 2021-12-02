from django.core.exceptions import ValidationError
from django.forms import Form, ModelChoiceField, Select

from service_catalog.models import Service


class NotificationServiceForm(Form):
    service = ModelChoiceField(queryset=Service.objects.all(),
                               widget=Select(attrs={'class': 'form-control'}))

    def __init__(self, user, *args, **kwargs):
        # get arguments from instance
        self.user = user
        super(NotificationServiceForm, self).__init__(*args, **kwargs)

    def clean_service(self):
        service = self.cleaned_data['service']
        if service in self.user.profile.subscribed_services_notification.all():
            raise ValidationError('You have already subscribed to this service')
        return service

    def save(self):
        service = self.cleaned_data["service"]
        self.user.profile.subscribed_services_notification.add(service)
        self.user.save()
