from django.forms import Form, FloatField


class QuotaBindingLimitForm(Form):
    def __init__(self, *args, **kwargs):
        self.billing_group = kwargs.pop('billing_group')
        super(QuotaBindingLimitForm, self).__init__(*args, **kwargs)
        for binding in self.billing_group.quota_bindings.all():
            self.fields[binding.quota_attribute_definition.name] = FloatField(initial=binding.limit, help_text=f"Define the limit for {binding.quota_attribute_definition.name}")
            self.fields[binding.quota_attribute_definition.name].widget.attrs['class'] = 'form-control'

    def save(self):
        for binding in self.billing_group.quota_bindings.all():
            binding.limit = self.cleaned_data.get(binding.quota_attribute_definition.name)
            binding.save()
