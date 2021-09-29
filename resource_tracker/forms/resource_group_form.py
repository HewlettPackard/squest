from taggit.forms import *
from resource_tracker.models import ResourceGroup
from utils.squest_model_form import SquestModelForm


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
