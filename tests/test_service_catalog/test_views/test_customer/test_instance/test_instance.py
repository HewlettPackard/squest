from django.contrib.auth.models import User
from django.urls import reverse
from guardian.shortcuts import get_objects_for_user

from profiles.models import Team
from service_catalog.forms.utils import get_choices_from_string
from service_catalog.models import Support, SupportMessage, Request, OperationType, Operation
from service_catalog.models.instance import InstanceState, Instance
from service_catalog.models.support import SupportState
from tests.test_service_catalog.base_test_request import BaseTestRequest


def _get_void_value(survey_field):
    if survey_field["type"] == "multiplechoice":
        return [get_choices_from_string(survey_field["choices"])[1][1]]
    elif survey_field["type"] == "multiselect":
        return get_choices_from_string(survey_field["choices"])[1][1]
    elif survey_field["type"] == "integer":
        return 0
    elif survey_field["type"] == "float":
        return 0.0
    else:
        return survey_field["type"]


class TestCustomerInstanceViews(BaseTestRequest):

    def setUp(self):
        super(TestCustomerInstanceViews, self).setUp()
        self.client.login(username=self.standard_user, password=self.common_password)

    def test_get_instance_list(self):
        url = reverse('service_catalog:instance_list')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), 1)

    def test_get_instance_details(self):
        self.test_instance.state = InstanceState.AVAILABLE
        self.test_instance.save()
        args = {
            "instance_id": self.test_instance.id
        }
        url = reverse('service_catalog:instance_details', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTrue("instance" in response.context)
        self.assertEqual(self.test_instance.name, response.context["instance"].name)

    def test_operation_list_is_filtered(self):
        self.test_instance.state = InstanceState.AVAILABLE
        self.test_instance.save()
        args = {
            "instance_id": self.test_instance.id
        }
        url = reverse('service_catalog:instance_details', kwargs=args)
        self.client.force_login(user=self.superuser)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data),
                         Operation.objects.filter(service=self.test_instance.service, type__in=[OperationType.UPDATE, OperationType.DELETE]).count())

        # set an operation to be admin only
        self.update_operation_test.is_admin_operation = True
        self.update_operation_test.save()

        # as an admin I still have the full list
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), Operation.objects.filter(service=self.test_instance.service, type__in=[OperationType.UPDATE, OperationType.DELETE]).count())

        # user does not see the admin operation
        self.client.force_login(user=self.standard_user)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), Operation.objects.filter(service=self.test_instance.service, type__in=[OperationType.UPDATE, OperationType.DELETE]).count() - 1)

    def test_non_owner_user_cannot_get_details(self):
        self.client.login(username=self.standard_user_2, password=self.common_password)
        args = {
            "instance_id": self.test_instance.id
        }
        url = reverse('service_catalog:instance_details', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    def test_create_new_support_on_instance(self):
        args = {
            "instance_id": self.test_instance.id
        }
        url = reverse('service_catalog:instance_new_support', kwargs=args)
        data = {
            "title": "test_support",
            "content": "test_support_content"
        }
        number_support_before = Support.objects.all().count()
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(number_support_before + 1, Support.objects.all().count())

    def test_create_new_support_on_instance_with_external_url(self):
        # add a url
        self.test_instance.service.external_support_url = "http://external_service"
        self.test_instance.service.save()
        args = {
            "instance_id": self.test_instance.id
        }
        url = reverse('service_catalog:instance_new_support', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual(self.test_instance.service.external_support_url, response.url)

        # test with URL that use a valid jinja
        self.test_instance.service.external_support_url = "http://external_service?instance_id={{ instance.id }}"
        self.test_instance.service.save()
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual(f"http://external_service?instance_id={self.test_instance.id}", response.url)

        # test with a non-existing instance flag
        self.test_instance.service.external_support_url = "http://external_service?instance_id={{ instance.unknown_flag }}"
        self.test_instance.service.save()
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual("http://external_service?instance_id=", response.url)

        # test with non-existing object
        self.test_instance.service.external_support_url = "http://external_service?instance_id={{ unknown_object.id }}"
        self.test_instance.service.save()
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        # we return the url with jinja parsed
        expected = "http://external_service?instance_id=%7B%7B%20unknown_object.id%20%7D%7D"
        self.assertEqual(expected, response.url)

    def test_cannot_create_new_support_on_non_owned_instance(self):
        self.client.login(username=self.standard_user_2, password=self.common_password)
        args = {
            "instance_id": self.test_instance.id
        }
        url = reverse('service_catalog:instance_new_support', kwargs=args)
        data = {
            "title": "test_support",
            "content": "test_support_content"
        }
        response = self.client.post(url, data=data)
        self.assertEqual(403, response.status_code)

    def test_get_customer_instance_support_details(self):
        args = {
            "instance_id": self.test_instance.id,
            "support_id": self.support_test.id
        }
        url = reverse('service_catalog:instance_support_details', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTrue("support" in response.context)
        self.assertEqual(self.support_test.title, response.context["support"].title)

    def test_get_customer_instance_support_details_non_owned_instance(self):
        self.client.login(username=self.standard_user_2, password=self.common_password)
        args = {
            "instance_id": self.test_instance.id,
            "support_id": self.support_test.id
        }
        url = reverse('service_catalog:instance_support_details', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    def test_close_instance_support(self):
        args = {
            "instance_id": self.test_instance.id,
            "support_id": self.support_test.id
        }
        url = reverse('service_catalog:instance_support_details', kwargs=args)
        data = {
            "btn_close": True
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.support_test.refresh_from_db()
        self.assertEqual(self.support_test.state, SupportState.CLOSED)

    def test_reopen_instance_support(self):
        self.support_test.state = SupportState.CLOSED
        self.support_test.save()
        args = {
            "instance_id": self.test_instance.id,
            "support_id": self.support_test.id
        }
        url = reverse('service_catalog:instance_support_details', kwargs=args)
        data = {
            "btn_re_open": True
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.support_test.refresh_from_db()
        self.assertEqual(self.support_test.state, SupportState.OPENED)

    def test_reopen_already_opened_instance_support(self):
        args = {
            "instance_id": self.test_instance.id,
            "support_id": self.support_test.id
        }
        url = reverse('service_catalog:instance_support_details', kwargs=args)
        data = {
            "btn_re_open": True
        }
        response = self.client.post(url, data=data)
        self.assertEqual(403, response.status_code)
        self.support_test.refresh_from_db()
        self.assertEqual(self.support_test.state, SupportState.OPENED)

    def _create_message(self, instance_id, support_id, message):
        args = {
            "instance_id": instance_id,
            "support_id": support_id
        }
        url = reverse('service_catalog:instance_support_details', kwargs=args)
        data = {
            "content": message
        }
        return self.client.post(url, data=data)

    def _edit_message(self, instance_id, support_id, message_id, message):
        args = {
            "instance_id": instance_id,
            "support_id": support_id,
            "message_id": message_id
        }
        url = reverse('service_catalog:support_message_edit', kwargs=args)
        data = {
            "content": message
        }
        return self.client.post(url, data=data)

    def test_add_message_to_existing_support(self):
        number_message_before = SupportMessage.objects.filter(support=self.support_test).count()
        response = self._create_message(self.test_instance.id, self.support_test.id, "new message")
        self.assertEqual(302, response.status_code)
        self.assertEqual(number_message_before + 1,
                         SupportMessage.objects.filter(support=self.support_test).count())

    def test_sender_can_edit_message(self):
        self._create_message(self.test_instance.id, self.support_test.id, "new message")
        message = SupportMessage.objects.last()
        self.assertEqual(message.content, "new message")
        self.assertEqual(message.sender, self.standard_user)
        response = self._edit_message(self.test_instance.id, self.support_test.id, message.id, "message edited")
        self.assertEqual(302, response.status_code)
        message.refresh_from_db()
        self.assertEqual(message.content, "message edited")
        self.assertEqual(message.sender, self.standard_user)


    def test_admin_can_edit_message(self):
        self._create_message(self.test_instance.id, self.support_test.id, "new message")
        message = SupportMessage.objects.last()
        self.assertEqual(message.content, "new message")
        self.assertEqual(message.sender, self.standard_user)
        self.client.force_login(self.superuser)
        response = self._edit_message(self.test_instance.id, self.support_test.id, message.id, "message edited")
        self.assertEqual(302, response.status_code)
        message.refresh_from_db()
        self.assertEqual(message.content, "message edited")
        self.assertEqual(message.sender, self.standard_user)

    def test_non_sender_cannot_edit_message(self):
        self._create_message(self.test_instance.id, self.support_test.id, "new message")
        message = SupportMessage.objects.last()
        self.assertEqual(message.content, "new message")
        self.assertEqual(message.sender, self.standard_user)
        self.client.force_login(self.standard_user_2)
        response = self._edit_message(self.test_instance.id, self.support_test.id, message.id, "message edited")
        self.assertEqual(403, response.status_code)
        message.refresh_from_db()
        self.assertEqual(message.content, "new message")
        self.assertEqual(message.sender, self.standard_user)

    def test_cannot_edit_message_when_logout(self):
        self._create_message(self.test_instance.id, self.support_test.id, "new message")
        message = SupportMessage.objects.last()
        self.assertEqual(message.content, "new message")
        self.assertEqual(message.sender, self.standard_user)
        self.client.logout()
        response = self._edit_message(self.test_instance.id, self.support_test.id, message.id, "message edited")
        self.assertEqual(302, response.status_code)
        message.refresh_from_db()
        self.assertEqual(message.content, "new message")
        self.assertEqual(message.sender, self.standard_user)

    def test_archive_instance(self):
        self.test_instance.state = InstanceState.DELETED
        self.test_instance.save()
        args = {
            "instance_id": self.test_instance.id
        }
        url = reverse('service_catalog:instance_archive', kwargs=args)
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        self.test_instance.refresh_from_db()
        self.assertEqual(self.test_instance.state, InstanceState.ARCHIVED)

    def test_cannot_archive_non_deleted_instance(self):
        self.test_instance.state = InstanceState.AVAILABLE
        args = {
            "instance_id": self.test_instance.id
        }
        url = reverse('service_catalog:instance_archive', kwargs=args)
        response = self.client.post(url)
        self.assertEqual(403, response.status_code)
        self.test_instance.refresh_from_db()
        self.assertEqual(self.test_instance.state, InstanceState.PENDING)

    def test_delete_support_instance_still_present(self):
        """
        Check that deleting a support will not delete the instance
        """
        self.support_test.delete()
        self.assertTrue(Instance.objects.filter(id=self.test_instance.id).exists())

    def test_delete_instance_do_delete_related_supports(self):
        instance_id = self.test_instance.id
        self.test_instance.delete()
        self.assertFalse(Support.objects.filter(instance=instance_id).exists())

    def test_add_and_remove_new_user_in_role_update_permissions_of_instance(self):
        user = User.objects.create(username="tester")
        for role in self.test_instance.roles:
            self.test_instance.add_user_in_role(user, role.name)
            self._assert_role_of_instance(user, self.test_instance, role.name)
            self.test_instance.remove_user_in_role(user, role.name)
            self._assert_role_of_instance(user, self.test_instance, None)

    def test_add_and_remove_new_team_in_role_update_permissions_of_instance(self):
        team_admin = User.objects.create(username="tester-admin")
        user = User.objects.create(username="tester")
        team = Team.objects.create(name="test")
        team.add_user_in_role(team_admin, "Admin")
        team.add_user_in_role(user, "Member")
        for role in self.test_instance.roles:
            self.test_instance.add_team_in_role(team, role.name)
            self._assert_role_of_instance(team_admin, self.test_instance, role.name)
            self._assert_role_of_instance(user, self.test_instance, role.name)
            self.test_instance.remove_team_in_role(team, role.name)
            self._assert_role_of_instance(team_admin, self.test_instance, None)
            self._assert_role_of_instance(user, self.test_instance, None)

    def test_add_and_remove_new_member_in_team_update_permissions_of_instance(self):
        team_admin = User.objects.create(username="tester-admin")
        user = User.objects.create(username="tester")
        tmp_user = User.objects.create(username="tester-tmp")
        team = Team.objects.create(name="test")
        team.add_user_in_role(team_admin, "Admin")
        team.add_user_in_role(user, "Member")
        for role in self.test_instance.roles:
            print(f"testing for the role: {role.name}")
            self.test_instance.add_team_in_role(team, role.name)
            self._assert_role_of_instance(tmp_user, self.test_instance, None)
            team.add_user_in_role(tmp_user, "Member")
            self._assert_role_of_instance(tmp_user, self.test_instance, role.name)
            team.remove_user_in_role(tmp_user, "Member")
            self._assert_role_of_instance(tmp_user, self.test_instance, None)
            self.test_instance.remove_team_in_role(team, role.name)


    def _assert_role_of_instance(self, user, instance, role_name):
        self.client.force_login(user)
        self.assertIn(role_name, [None, "Admin", "Operator", "Reader"])
        self._assert_list_instances(instance, role_name in ["Admin", "Operator", "Reader"])
        self._assert_get_instance_details(instance, role_name in ["Admin", "Operator", "Reader"])
        self._assert_request_operation_on_instance(instance, role_name in ["Admin", "Operator"])
        self._assert_request_instance_support(instance, role_name in ["Admin", "Operator"])
        self._assert_archive_instance(instance, role_name in ["Admin"])

    def _assert_list_instances(self, instance, authorized=True):
        url = reverse('service_catalog:instance_list')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        logged_user = User.objects.get(id=self.client.session['_auth_user_id'])
        if authorized:
            self.assertTrue(instance in get_objects_for_user(logged_user, 'service_catalog.view_instance'))
        else:
            self.assertFalse(instance in get_objects_for_user(logged_user, 'service_catalog.view_instance'))
        self.assertEqual(len(response.context["table"].data.data),
                         get_objects_for_user(logged_user, 'service_catalog.view_instance').count())

    def _assert_get_instance_details(self, instance, authorized=True):
        status = 200 if authorized else 403
        args = {
            "instance_id": instance.id
        }
        url = reverse('service_catalog:instance_details', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(status, response.status_code)

    def _assert_request_operation_on_instance(self, instance, authorized=True):
        if instance.state != InstanceState.AVAILABLE:
            instance.state = InstanceState.AVAILABLE
            instance.save()
        current_request_number = Request.objects.all().count()
        expected_request_number = current_request_number + 1 if authorized else current_request_number
        status = 302 if authorized else 403
        operation = Operation.objects.filter(service=instance.service,
                                          type__in=[OperationType.UPDATE, OperationType.DELETE]).first()
        args = {
            'instance_id': instance.id,
            'operation_id': operation.id
        }
        data = dict()
        if "spec" in operation.job_template.survey:
            for field in operation.job_template.survey["spec"]:
                data[field["variable"]] = _get_void_value(field)
            url = reverse('service_catalog:instance_request_new_operation', kwargs=args)
            response = self.client.post(url, data=data)
            self.assertEqual(status, response.status_code)
            self.assertEqual(expected_request_number, Request.objects.all().count())

    def _assert_request_instance_support(self, instance, authorized=True):
        status = 302 if authorized else 403
        args = {
            "instance_id": instance.id
        }
        url = reverse('service_catalog:instance_new_support', kwargs=args)
        data = {
            "title": "test_support",
            "content": "test_support_content"
        }
        number_support_before = Support.objects.all().count()
        response = self.client.post(url, data=data)
        self.assertEqual(status, response.status_code)
        expected_support_number = number_support_before + 1 if authorized else number_support_before
        self.assertEqual(expected_support_number, Support.objects.all().count())

    def _assert_archive_instance(self, instance, authorized=True):
        if instance.state != InstanceState.DELETED:
            instance.state = InstanceState.DELETED
            instance.save()
        status = 302 if authorized else 403
        args = {
            "instance_id": instance.id
        }
        url = reverse('service_catalog:instance_archive', kwargs=args)
        response = self.client.post(url)
        self.assertEqual(status, response.status_code)
        if authorized:
            instance.refresh_from_db()
            self.assertEqual(instance.state, InstanceState.ARCHIVED)
