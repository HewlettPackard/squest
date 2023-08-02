from django import forms
from django.forms import IntegerField

from Squest.utils.squest_form import SquestForm
from profiles.models import Quota
from resource_tracker_v2.models import AttributeDefinition


class QuotaForm(SquestForm):

    def __init__(self, *args, **kwargs):
        self.scope = kwargs.pop("scope")
        super(QuotaForm, self).__init__(*args, **kwargs)
        class_name = self.scope.get_object().__class__.__name__

        if class_name == "Organization":
            # create a field for each attribute definition
            all_attributes = AttributeDefinition.objects.all()
            if not all_attributes.exists():
                self.help_text = f"To set quotas in an organization, you need first to create attributes"
            for attribute_definition in all_attributes:
                # get the value if exist already
                current_quota = Quota.objects.filter(scope=self.scope, attribute_definition=attribute_definition).first()
                default_value = current_quota.limit if current_quota is not None else None
                self.fields[f"attribute_definition_{attribute_definition.id}"] = \
                    IntegerField(label=attribute_definition.name,
                                 min_value=0,
                                 required=False,
                                 initial=default_value,
                                 widget=forms.NumberInput(attrs={'step': '1',
                                                                 'class': 'form-control'}))
        elif class_name == "Team":
            target_team = self.scope.get_object()
            all_quotas = Quota.objects.filter(scope_id=target_team.org.id)
            if not all_quotas.exists():
                self.help_text = f"To set quotas in a team, you need first to set quotas on the parent organization"
            for quota in all_quotas:
                # get the value if exist already for the team
                current_quota = Quota.objects.filter(scope=self.scope,
                                                     attribute_definition=quota.attribute_definition).first()
                default_value = current_quota.limit if current_quota is not None else None
                self.fields[f"attribute_definition_{quota.attribute_definition.id}"] = \
                    IntegerField(label=quota.attribute_definition.name,
                                 required=False,
                                 initial=default_value,
                                 max_value=quota.available,
                                 help_text=f"Available a organization level: {quota.available}",
                                 widget=forms.NumberInput(attrs={'step': '1',
                                                                 'class': 'form-control'}))

    def save(self):
        for form_attribute, limit in self.cleaned_data.items():
            attribute_id = form_attribute.split("attribute_definition_")[1]
            initial_value = Quota.objects.filter(scope=self.scope, attribute_definition_id=int(attribute_id)).first()
            if initial_value:
                initial_value.limit = limit
                initial_value.save()
            else:
                if limit is not None:
                    Quota.objects.create(scope=self.scope, attribute_definition_id=int(attribute_id), limit=limit)
