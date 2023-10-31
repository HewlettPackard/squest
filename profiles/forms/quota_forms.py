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
                current_quota = Quota.objects.filter(scope=self.scope,
                                                     attribute_definition=attribute_definition).first()
                default_value = None
                consumed = 0
                if current_quota is not None:
                    default_value = current_quota.limit
                    consumed = current_quota.consumed
                else:
                    current_quota = Quota(scope=self.scope, attribute_definition=attribute_definition)
                    consumed = current_quota.consumed

                self.fields[f"attribute_definition_{attribute_definition.id}"] = \
                    IntegerField(label=attribute_definition.name,
                                 min_value=consumed,
                                 required=False,
                                 initial=default_value,
                                 help_text=f"Already consumed: {consumed}",
                                 widget=forms.NumberInput(attrs={'step': '1',
                                                                 'class': 'form-control'}))
        elif class_name == "Team":
            target_team = self.scope.get_object()
            all_quotas_at_org_level = Quota.objects.filter(scope_id=target_team.org.id)
            if not all_quotas_at_org_level.exists():
                self.help_text = f"To set quotas in a team, you need first to set quotas on the parent organization"
            for parent_quota in all_quotas_at_org_level:
                # get the value if exist already for the team
                current_quota = Quota.objects.filter(scope=self.scope,
                                                     attribute_definition=parent_quota.attribute_definition).first()
                consumed = 0
                default_value = 0
                if current_quota:
                    consumed = current_quota.consumed
                    default_value = current_quota.limit
                else:
                    current_quota = Quota(scope=self.scope, attribute_definition=parent_quota.attribute_definition)
                    consumed = current_quota.consumed
                max_value = parent_quota.available + default_value
                self.fields[f"attribute_definition_{parent_quota.attribute_definition.id}"] = \
                    IntegerField(label=parent_quota.attribute_definition.name,
                                 required=False,
                                 initial=default_value,
                                 min_value=consumed,
                                 max_value=max_value,
                                 help_text=f"Available at organization level: {max_value}",
                                 widget=forms.NumberInput(attrs={'step': '1',
                                                                 'class': 'form-control'}))

    def save(self):
        for form_attribute, limit in self.cleaned_data.items():
            attribute_id = form_attribute.split("attribute_definition_")[1]
            initial_value = Quota.objects.filter(scope=self.scope, attribute_definition_id=int(attribute_id)).first()
            if initial_value:
                if limit is None:
                    initial_value.delete()
                else:
                    initial_value.limit = limit
                    initial_value.save()
            else:
                if limit is not None:
                    Quota.objects.create(scope=self.scope, attribute_definition_id=int(attribute_id), limit=limit)
