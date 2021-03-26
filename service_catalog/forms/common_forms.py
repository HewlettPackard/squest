from django import forms
from django.forms import ModelForm
from service_catalog.models import Message, Request


class RequestMessageForm(ModelForm):
    content = forms.CharField(label="Add a comment",
                              required=True,
                              help_text="Markdown supported",
                              widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = Message
        fields = ["content"]
