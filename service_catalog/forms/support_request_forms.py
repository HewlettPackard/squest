import urllib3
from django import forms

from service_catalog.models import Instance, Support, SupportMessage

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FIRST_BLOCK_FORM_FIELD_TITTLE = "1. Squest fields"


class SupportRequestForm(forms.Form):
    title = forms.CharField(label="Title",
                            widget=forms.TextInput(attrs={'class': 'form-control'}))

    content = forms.CharField(label="Add a comment",
                              help_text="Markdown supported",
                              widget=forms.Textarea(attrs={'class': 'form-control'}))

    def __init__(self, user, *args, **kwargs):
        # get arguments from instance
        self.user = user
        instance_id = kwargs.pop('instance_id', None)
        super(SupportRequestForm, self).__init__(*args, **kwargs)
        self.instance = Instance.objects.get(id=instance_id)

    def save(self):
        title = self.cleaned_data["title"]
        content = self.cleaned_data["content"]
        # open a new support case
        new_support = Support.objects.create(title=title,
                                             instance=self.instance,
                                             opened_by=self.user)

        message = SupportMessage.objects.create(content=content, sender=self.user, support=new_support)
        from service_catalog.mail_utils import send_mail_new_support_message
        send_mail_new_support_message(message)
        return message
