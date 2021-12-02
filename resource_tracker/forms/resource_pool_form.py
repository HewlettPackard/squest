from taggit.forms import *
from resource_tracker.models import ResourcePool
from Squest.utils.squest_model_form import SquestModelForm

class ResourcePoolForm(SquestModelForm):
    class Meta:
        model = ResourcePool
        fields = ["name", "tags"]

    name = forms.CharField(label="Name",
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    tags = TagField(label="Tags",
                    required=False,
                    help_text="Comma-separated list of tags (more details in documentation)",
                    widget=TagWidget())
