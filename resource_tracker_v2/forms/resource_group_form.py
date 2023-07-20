from django import forms
from taggit.forms import TagField, TagWidget

from Squest.utils.squest_model_form import SquestModelForm
from resource_tracker_v2.models import ResourceGroup


class ResourceGroupForm(SquestModelForm):
    class Meta:
        model = ResourceGroup
        fields = ["name", "tags"]

    name = forms.CharField(label="Name",
                           widget=forms.TextInput())

    tags = TagField(label="Tags",
                    required=False,
                    help_text="Comma-separated list of tags (more details in documentation)",
                    widget=TagWidget())
