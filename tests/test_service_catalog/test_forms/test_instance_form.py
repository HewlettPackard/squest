from profiles.models import Permission
from service_catalog.forms import InstanceFormRestricted
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestInstanceForm(BaseTestRequest):

    def setUp(self):
        super(TestInstanceForm, self).setUp()

    def test_instance_form_restricted_with_admin(self):
        parameters = {
            'instance': self.test_instance,
            'user': self.standard_user
        }
        data = {
            'name': 'test_instance_updated',
            'requester': self.standard_user_2,
        }
        form = InstanceFormRestricted(data, **parameters)
        self.assertTrue(form.is_valid())
        self.assertFalse('name' in form.fields)
        self.assertFalse('requester' in form.fields)
        self.team_member_role.permissions.add(
            Permission.objects.get_by_natural_key(codename="rename_instance",
                                                  app_label="service_catalog",
                                                  model="instance"))
        form = InstanceFormRestricted(data, **parameters)
        self.assertTrue(form.is_valid())
        self.assertTrue('name' in form.fields)
        self.assertFalse('requester' in form.fields)
        self.team_member_role.permissions.add(
            Permission.objects.get_by_natural_key(codename="change_requester_on_instance",
                                                  app_label="service_catalog",
                                                  model="instance"))
        form = InstanceFormRestricted(data, **parameters)
        self.assertTrue('name' in form.fields)
        self.assertTrue('requester' in form.fields)
        # standard user 2 not part of the team yet so not a valid choice
        self.assertFalse(form.is_valid())
        # add standard user 2 to the team
        self.test_quota_scope.add_user_in_role(self.standard_user_2, self.team_member_role)
        self.test_quota_scope_team.add_user_in_role(self.standard_user_2, self.team_member_role)
        form = InstanceFormRestricted(data, **parameters)
        self.assertIn(self.standard_user_2, list(form.fields["requester"].queryset))
        self.assertTrue(form.is_valid())
