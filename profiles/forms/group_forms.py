from django.contrib.auth.models import Group, User
from django.forms import MultipleChoiceField, SelectMultiple, Form

from Squest.utils.squest_model_form import SquestModelForm


class AddUserForm(Form):
    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group')
        super(AddUserForm, self).__init__(*args, **kwargs)
        self.fields['users'].choices = [(user.id, user.username) for user in User.objects.all()]
        self.fields['users'].initial = [user.id for user in self.group.user_set.all()]

    users = MultipleChoiceField(label="Users",
                                required=False,
                                choices=[],
                                widget=SelectMultiple(attrs={'class': 'selectpicker', 'data-live-search': "true"})
                                )

    def save(self):
        current_users = self.group.user_set.all()
        users_id = self.cleaned_data.get('users')
        selected_users = [User.objects.get(id=user_id) for user_id in users_id]
        to_remove = list(set(current_users) - set(selected_users))
        to_add = list(set(selected_users) - set(current_users))
        for user in to_remove:
            self.group.user_set.remove(user)
        for user in to_add:
            self.group.user_set.add(user)


class GroupForm(SquestModelForm):
    class Meta:
        model = Group
        fields = ["name"]


from django.contrib.auth.models import Group, User
from django.forms import MultipleChoiceField, SelectMultiple, CharField

from Squest.utils.squest_form import SquestForm


class CustomGroupForm(SquestForm):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.group = kwargs['instance']
        self.fields['users'].choices = [(user.id, user.username) for user in User.objects.all()]
        self.fields['users'].initial = [user.id for user in self.group.user_set.all()]
        self.fields['name'].initial = self.group.name

    name = CharField()
    users = MultipleChoiceField(label="Users",
                                required=False,
                                choices=[]
                                )

    def save(self):
        self.group.name = self.cleaned_data.get('name')
        current_users = self.group.user_set.all()
        users_id = self.cleaned_data.get('users')
        selected_users = [User.objects.get(id=user_id) for user_id in users_id]
        to_remove = list(set(current_users) - set(selected_users))
        to_add = list(set(selected_users) - set(current_users))
        for user in to_remove:
            self.group.user_set.remove(user)
        for user in to_add:
            self.group.user_set.add(user)
        self.group.save()


from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User, Group
from django.forms import ModelMultipleChoiceField
from django_filters.fields import MultipleChoiceField

from profiles.models import Organization
from Squest.utils.squest_model_form import SquestModelForm


class UsersGroupForm(SquestForm):
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        super(UsersGroupForm, self).__init__(*args, **kwargs)
        self.fields['users'].choices = [(user.id, user.username) for user in User.objects.all()]
        self.fields['users'].initial = [user.id for user in self.instance.user_set.all()]

    users = MultipleChoiceField(label="Users",
                                required=False,
                                choices=[]
                                )

    def save(self):
        current_users = self.instance.user_set.all()
        users_id = self.cleaned_data.get('users')
        selected_users = [User.objects.get(id=user_id) for user_id in users_id]
        to_remove = list(set(current_users) - set(selected_users))
        to_add = list(set(selected_users) - set(current_users))
        for user in to_remove:
            self.instance.user_set.remove(user)
        for user in to_add:
            self.instance.user_set.add(user)
        return self.instance
