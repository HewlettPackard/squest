from django.forms import Form, FloatField


class QuotaBindingLimitForm(Form):
    def __init__(self, *args, **kwargs):
        self.billing_group = kwargs.pop('billing_group')
        super(QuotaBindingLimitForm, self).__init__(*args, **kwargs)
        for binding in self.billing_group.quota_bindings.all():
            self.fields[binding.quota.name] = FloatField(initial=binding.limit, help_text=f"Define the limit for {binding.quota.name}")
            self.fields[binding.quota.name].widget.attrs['class'] = 'form-control'

    def save(self):
        for binding in self.billing_group.quota_bindings.all():
            binding.limit = self.cleaned_data.get(binding.quota.name)
            binding.save()
