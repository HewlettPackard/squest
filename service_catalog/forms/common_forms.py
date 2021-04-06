from django import forms
from django.forms import ModelForm

from service_catalog.models import RequestMessage, SupportMessage


class RequestMessageForm(ModelForm):
    content = forms.CharField(label="Add a comment",
                              required=True,
                              help_text="Markdown supported",
                              widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = RequestMessage
        fields = ["content"]


class SupportMessageForm(ModelForm):
    content = forms.CharField(label="Add a comment",
                              required=False,
                              help_text="Markdown supported",
                              widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = SupportMessage
        fields = ["content"]
