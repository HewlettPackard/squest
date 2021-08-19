from django import forms
from django.contrib.auth.models import Group, User


class AddUserForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.current_users = kwargs.pop('current_users')
        super(AddUserForm, self).__init__(*args, **kwargs)
        self.fields['users'].choices = [(user.id, user.username) for user in User.objects.all()]
        self.fields['users'].initial = [user.id for user in self.current_users]

    users = forms.MultipleChoiceField(label="Users",
                                      required=False,
                                      choices=[],
                                      widget=forms.CheckboxSelectMultiple(attrs={'class': 'disable_list_style'})
                                      )


class GroupForm(forms.ModelForm):
    name = forms.CharField(label="Name",
                           widget=forms.TextInput(attrs={'class': 'form-control'})
                           )

    class Meta:
        model = Group
        fields = ["name"]
