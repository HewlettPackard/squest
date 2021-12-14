from django import forms

from service_catalog.models import RequestMessage, SupportMessage
from Squest.utils.squest_model_form import SquestModelForm


class RequestMessageForm(SquestModelForm):
    class Meta:
        model = RequestMessage
        fields = ["content"]

    content = forms.CharField(label="Add a comment",
                              help_text="Markdown supported",
                              widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender')
        self.request = kwargs.pop('target_request')
        super(RequestMessageForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        message = super(RequestMessageForm, self).save(commit=False)
        message.request = self.request
        message.sender = self.sender
        return message.save()


class SupportMessageForm(SquestModelForm):
    class Meta:
        model = SupportMessage
        fields = ["content"]

    content = forms.CharField(label="Add a comment",
                              required=False,
                              help_text="Markdown supported",
                              widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender')
        self.support = kwargs.pop('support')
        super(SupportMessageForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        message = super(SupportMessageForm, self).save(commit=False)
        message.support = self.support
        message.sender = self.sender
        return message.save()
