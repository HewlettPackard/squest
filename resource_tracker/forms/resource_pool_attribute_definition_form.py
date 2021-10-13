from django.core.exceptions import ValidationError
from taggit.forms import *
from resource_tracker.models import ResourcePoolAttributeDefinition
from utils.squest_model_form import SquestModelForm


class ResourcePoolAttributeDefinitionForm(SquestModelForm):
    class Meta:
        model = ResourcePoolAttributeDefinition
        fields = ["name", "over_commitment_producers", "over_commitment_consumers"]

    name = forms.CharField(label="Name",
                           widget=forms.TextInput())
    over_commitment_producers = forms.FloatField(label="Over commitment for producers",
                                                 required=False,
                                                 initial=ResourcePoolAttributeDefinition._meta.get_field(
                                                     'over_commitment_producers').default,
                                                 help_text="All producers will produce X times more",

                                                 widget=forms.NumberInput(
                                                     attrs={'step': '0.01'}))

    over_commitment_consumers = forms.FloatField(label="Over commitment for consumers",
                                                 required=False,
                                                 initial=ResourcePoolAttributeDefinition._meta.get_field(
                                                     'over_commitment_consumers').default,

                                                 help_text="All consumers will consume X times more",
                                                 widget=forms.NumberInput(
                                                     attrs={'step': '0.01'}))

    def clean_over_commitment_producers(self):
        data = self.cleaned_data['over_commitment_producers']
        if not data:
            data = ResourcePoolAttributeDefinition._meta.get_field('over_commitment_producers').default
        return data

    def clean_over_commitment_consumers(self):
        data = self.cleaned_data['over_commitment_consumers']
        if not data:
            data = ResourcePoolAttributeDefinition._meta.get_field('over_commitment_consumers').default
        return data

    def clean(self):
        cleaned_data = self.cleaned_data
        if hasattr(self, 'resource_pool'):
            if ResourcePoolAttributeDefinition.objects.filter(name=cleaned_data['name'],
                                                              resource_pool=self.resource_pool).exists():
                raise ValidationError({'name': ["Attribute with this name already exists for this resource pool", ]})

        # Always return cleaned_data
        return cleaned_data
