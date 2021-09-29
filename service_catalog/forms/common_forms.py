from django import forms

from service_catalog.models import RequestMessage, SupportMessage
from utils.squest_model_form import SquestModelForm


class RequestMessageForm(SquestModelForm):
    content = forms.CharField(label="Add a comment",
                              help_text="Markdown supported",
                              widget=forms.Textarea())

    class Meta:
        model = RequestMessage
        fields = ["content"]


class SupportMessageForm(SquestModelForm):
    content = forms.CharField(label="Add a comment",
                              required=False,
                              help_text="Markdown supported",
                              widget=forms.Textarea())

    class Meta:
        model = SupportMessage
        fields = ["content"]
