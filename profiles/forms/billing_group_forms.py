from django import forms

from profiles.models import BillingGroup


class BillingGroupForm(forms.ModelForm):
    name = forms.CharField(label="Name",
                           widget=forms.TextInput(attrs={'class': 'form-control'})
                           )

    class Meta:
        model = BillingGroup
        fields = ["name"]
