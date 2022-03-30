from django import forms

from service_catalog.models import SupportMessage
from Squest.utils.squest_model_form import SquestModelForm


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
        from service_catalog.mail_utils import send_mail_new_support_message
        send_mail_new_support_message(message)
        return message.save()

