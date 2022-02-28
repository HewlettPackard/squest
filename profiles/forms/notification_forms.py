from django.forms import Form, SelectMultiple
from django_filters.fields import ModelMultipleChoiceField

from service_catalog.models import Service


class NotificationServiceForm(Form):
    service = ModelMultipleChoiceField(queryset=Service.objects.all(),
                                       widget=SelectMultiple(attrs={'class': 'form-control selectpicker',
                                                                    'data-live-search': 'true'}))

    def __init__(self, user, *args, **kwargs):
        # get arguments from instance
        self.user = user
        super(NotificationServiceForm, self).__init__(*args, **kwargs)
        self.fields['service'].initial = [service.id for service in self.user.profile.subscribed_services_notification.all()]

    def save(self):
        service_list = self.cleaned_data.get('service')
        current_service = [service.id for service in self.user.profile.subscribed_services_notification.all()]
        to_remove = list(set(current_service) - set(service_list))
        to_add = list(set(service_list) - set(current_service))
        for service in to_remove:
            self.user.profile.subscribed_services_notification.remove(service)
        for service in to_add:
            self.user.profile.subscribed_services_notification.add(service)
        self.user.save()
