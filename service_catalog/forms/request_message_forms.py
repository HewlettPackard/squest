from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models import RequestMessage


class RequestMessageForm(SquestModelForm):
    class Meta:
        model = RequestMessage
        fields = ["content"]

    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender')
        self.request = kwargs.pop('target_request')
        super(RequestMessageForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        message = super(RequestMessageForm, self).save(commit=False)
        message.request = self.request
        message.sender = self.sender
        message.save()
        return message
