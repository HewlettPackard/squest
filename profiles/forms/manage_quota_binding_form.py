from django.forms import Form, MultipleChoiceField, SelectMultiple

from profiles.models import Quota, QuotaBinding


class ManageQuotaBindingForm(Form):
    quota = MultipleChoiceField(label="Quota attributes",
                                                     required=False,
                                                     choices=[],
                                                     widget=SelectMultiple(
                                                         attrs={'class': 'selectpicker', 'data-live-search': "true"}
                                                     )
                                                     )

    def __init__(self, *args, **kwargs):
        self.billing_group = kwargs.pop('billing_group')
        self.initial_attribute = [binding.quota for binding in self.billing_group.quota_bindings.all()]
        super(ManageQuotaBindingForm, self).__init__(*args, **kwargs)
        self.fields['quota'].choices = [(billing_group.id, billing_group.name) for billing_group in
                                                             Quota.objects.all()]
        self.fields['quota'].initial = [billing_group.id for billing_group in self.initial_attribute]

    def save(self):
        id_list = self.cleaned_data.get('quota')
        selected = [Quota.objects.get(id=attribute_id) for attribute_id in id_list]
        to_remove = list(set(self.initial_attribute) - set(selected))
        to_add = list(set(selected) - set(self.initial_attribute))
        for attribute in to_remove:
            QuotaBinding.objects.filter(quota=attribute, billing_group=self.billing_group).delete()
        for attribute in to_add:
            QuotaBinding.objects.create(quota=attribute, billing_group=self.billing_group)
