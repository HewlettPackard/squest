from django.forms import ModelForm
from taggit.forms import *
from resource_tracker.models import ResourceGroup


class ResourceGroupForm(ModelForm):
    class Meta:
        model = ResourceGroup
        fields = ["name", "tags"]

    name = forms.CharField(label="Name",
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    tags = TagField(label="Tags",
                    required=False,
                    help_text="Comma-separated list of tags (more details in documentation)",
                    widget=TagWidget(attrs={'class': 'form-control'}))
