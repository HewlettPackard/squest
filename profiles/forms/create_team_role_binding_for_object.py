from django.forms import Form, ChoiceField, Select


class CreateTeamRoleBindingForObjectForm(Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.content_type = kwargs.pop('content_type')
        from profiles.views import get_objects_of_user_from_content_type, get_roles_from_content_type
        self.object = get_objects_of_user_from_content_type(self.user, self.content_type[0][0])
        self.role = get_roles_from_content_type(self.content_type[0][0])
        super(CreateTeamRoleBindingForObjectForm, self).__init__(*args, **kwargs)
        self.fields['content_type'].choices = self.content_type
        self.fields['content_type'].initial = self.content_type[0][0]
        self.fields['object'].choices = self.object
        self.fields['object'].initial = self.object[0][0]
        self.fields['role'].choices = self.role
        self.fields['role'].initial = self.role[0][0]

    content_type = ChoiceField(label="Type",
                               required=False,
                               choices=[],
                               widget=Select(attrs={'class': 'selectpicker', 'data-live-search': "true"})
                               )

    object = ChoiceField(label="Object",
                         required=False,
                         choices=[],
                         widget=Select(attrs={'class': 'selectpicker', 'data-live-search': "true"})
                         )

    role = ChoiceField(label="Role",
                       required=False,
                       choices=[],
                       widget=Select(attrs={'class': 'selectpicker', 'data-live-search': "true"})
                       )

    def full_clean(self):
        content_type_id = self.data.get('content_type')
        if isinstance(content_type_id, str):
            content_type_id = int(content_type_id)
            from profiles.views import get_objects_of_user_from_content_type, get_roles_from_content_type
            self.object = get_objects_of_user_from_content_type(self.user, content_type_id)
            self.role = get_roles_from_content_type(content_type_id)
            self.fields['object'].choices = self.object
            self.fields['role'].choices = self.role
        super(CreateTeamRoleBindingForObjectForm, self).full_clean()
