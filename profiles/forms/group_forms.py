from django.contrib.auth.models import Group, User
from django.forms import MultipleChoiceField, SelectMultiple, Form

from Squest.utils.squest_model_form import SquestModelForm

class AddUserForm(Form):
    def __init__(self, *args, **kwargs):
        self.current_users = kwargs.pop('current_users')
        super(AddUserForm, self).__init__(*args, **kwargs)
        self.fields['users'].choices = [(user.id, user.username) for user in User.objects.all()]
        self.fields['users'].initial = [user.id for user in self.current_users]

    users = MultipleChoiceField(label="Users",
                                required=False,
                                choices=[],
                                widget=SelectMultiple(attrs={'class': 'selectpicker', 'data-live-search': "true"})
                                )


class GroupForm(SquestModelForm):
    class Meta:
        model = Group
        fields = ["name"]
