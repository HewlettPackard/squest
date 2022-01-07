from django.forms import Form, MultipleChoiceField, SelectMultiple

from profiles.models import QuotaAttributeDefinition, QuotaBinding


class ManageQuotaBindingForm(Form):
    quota_attribute_definition = MultipleChoiceField(label="Quota attributes",
                                                     required=False,
                                                     choices=[],
                                                     widget=SelectMultiple(
                                                         attrs={'class': 'selectpicker', 'data-live-search': "true"}
                                                     )
                                                     )

    def __init__(self, *args, **kwargs):
        self.billing_group = kwargs.pop('billing_group')
        self.initial_attribute = [binding.quota_attribute_definition for binding in self.billing_group.quota_bindings.all()]
        super(ManageQuotaBindingForm, self).__init__(*args, **kwargs)
        self.fields['quota_attribute_definition'].choices = [(billing_group.id, billing_group.name) for billing_group in
                                                             QuotaAttributeDefinition.objects.all()]
        self.fields['quota_attribute_definition'].initial = [billing_group.id for billing_group in self.initial_attribute]

    def save(self):
        id_list = self.cleaned_data.get('quota_attribute_definition')
        selected = [QuotaAttributeDefinition.objects.get(id=attribute_id) for attribute_id in id_list]
        to_remove = list(set(self.initial_attribute) - set(selected))
        to_add = list(set(selected) - set(self.initial_attribute))
        for attribute in to_remove:
            QuotaBinding.objects.filter(quota_attribute_definition=attribute, billing_group=self.billing_group).delete()
        for attribute in to_add:
            QuotaBinding.objects.create(quota_attribute_definition=attribute, billing_group=self.billing_group)
