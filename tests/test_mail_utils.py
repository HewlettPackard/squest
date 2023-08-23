from django.contrib.contenttypes.models import ContentType

from profiles.models import RequestNotification, InstanceNotification, Role, Permission
from service_catalog.mail_utils import _get_subject, _get_headers, \
    _get_receivers_for_request_message, _get_receivers_for_support_message, _get_receivers_for_request, \
    _get_receivers_for_support

from service_catalog.models import RequestMessage, Instance, Request, SupportMessage, Support
from tests.test_service_catalog.base import BaseTest


class TestMailUtils(BaseTest):

    def setUp(self):
        super(TestMailUtils, self).setUp()
        data = {
            'text_variable': 'my_var',
            'multiplechoice_variable': 'choice1', 'multiselect_var': 'multiselect_1',
            'textarea_var': '2',
            'password_var': 'pass',
            'integer_var': '1',
            'float_var': '0.6'
        }
        self.test_instance = Instance.objects.create(name="test_instance_1",
                                                     service=self.service_test,
                                                     spec={
                                                         "value1": "key1"
                                                     },
                                                     requester=self.standard_user,
                                                     quota_scope=self.test_quota_scope)
        self.test_instance_2 = Instance.objects.create(name="test_instance_2",
                                                       service=self.service_test_2,
                                                       requester=self.standard_user,
                                                       quota_scope=self.test_quota_scope)
        self.test_request = Request.objects.create(fill_in_survey=data,
                                                   instance=self.test_instance,
                                                   operation=self.create_operation_test,
                                                   user=self.standard_user)
        self.test_request_2 = Request.objects.create(fill_in_survey=data,
                                                     instance=self.test_instance_2,
                                                     operation=self.create_operation_test_2,
                                                     user=self.standard_user)

        self.test_support = Support.objects.create(instance=self.test_instance)

        view_requestmessage_role = Role.objects.create(name="view_requestmessage_role")
        view_requestmessage_role.permissions.add(
            Permission.objects.get(
                codename="view_requestmessage",
                content_type=ContentType.objects.get_for_model(RequestMessage)
            )
        )
        self.test_quota_scope.add_user_in_role(self.standard_user, view_requestmessage_role)

        view_supportmessage_role = Role.objects.create(name="view_supportmessage_role")
        view_supportmessage_role.permissions.add(
            Permission.objects.get(
                codename="view_supportmessage",
                content_type=ContentType.objects.get_for_model(SupportMessage)
            )
        )
        self.test_quota_scope.add_user_in_role(self.standard_user, view_supportmessage_role)

    def test_get_admin_emails_with_request(self):
        # Test 1 - admin disabled notification
        self.superuser.profile.request_notification_enabled = False
        self.superuser.save()
        self.superuser_2.profile.request_notification_enabled = False
        self.superuser_2.save()
        self.assertEquals(0, len(_get_receivers_for_request(self.test_request)))

        # Test 2 - admin enabled notification
        self.superuser.profile.request_notification_enabled = True
        self.superuser.save()
        self.superuser_2.profile.request_notification_enabled = True
        self.superuser_2.save()
        self.assertCountEqual([self.superuser.email, self.superuser_2.email],
                              _get_receivers_for_request(self.test_request))

    def test_get_admin_emails_with_support(self):
        # Test 1 - admin disabled notification
        self.superuser.profile.instance_notification_enabled = False
        self.superuser.save()
        self.superuser_2.profile.instance_notification_enabled = False
        self.superuser_2.save()
        self.assertEquals(0, len(_get_receivers_for_support(self.test_support)))

        # Test 2 - admin enabled notification
        self.superuser.profile.instance_notification_enabled = True
        self.superuser.save()
        self.superuser_2.profile.instance_notification_enabled = True
        self.superuser_2.save()
        self.assertCountEqual([self.superuser.email, self.superuser_2.email],
                              _get_receivers_for_request(self.test_request))

    def test_get_admin_emails_with_request_filter(self):
        self.superuser.profile.request_notification_enabled = True
        self.superuser.save()
        self.superuser_2.profile.request_notification_enabled = False
        self.superuser_2.save()
        request_filter = RequestNotification.objects.create(name="test_filter",
                                                            profile=self.superuser.profile,
                                                            when="request.fill_in_survey['text_variable'] == 'my_var'")
        self.assertCountEqual([self.superuser.email], _get_receivers_for_request(self.test_request))
        request_filter.when = "request.fill_in_survey['text_variable'] == 'other_my_var'"
        request_filter.save()
        self.assertEquals(0, len(_get_receivers_for_request(self.test_request)))

    def test_get_admin_emails_with_instance_filter(self):
        self.superuser.profile.instance_notification_enabled = True
        self.superuser.save()
        self.superuser_2.profile.instance_notification_enabled = False
        self.superuser_2.save()
        instance_filter = InstanceNotification.objects.create(name="test_filter",
                                                              profile=self.superuser.profile,
                                                              when="instance.spec['value1'] == 'key1'")
        self.assertCountEqual([self.superuser.email], _get_receivers_for_support(self.test_support))
        instance_filter.when = "instance.spec['value1'] == 'other_key'"
        instance_filter.save()
        self.assertEquals(0, len(_get_receivers_for_support(self.test_support)))

    def test_get_headers(self):
        expected_list = ["Message-ID", "In-Reply-To", "References"]
        subject = _get_subject(self.test_instance)
        headers = _get_headers(subject)
        subject = _get_subject(self.test_instance_2)
        headers_2 = _get_headers(subject)
        for expected_key in expected_list:
            self.assertIn(expected_key, headers)
            self.assertNotEqual(headers[expected_key], headers_2[expected_key])

    def test_get_subject(self):
        subject_instance = _get_subject(self.test_instance)
        subject_instance_2 = _get_subject(self.test_instance_2)
        self.assertNotEqual(subject_instance, subject_instance_2)
        subject_request = _get_subject(self.test_request)
        subject_request_2 = _get_subject(self.test_request_2)
        self.assertNotEqual(subject_request, subject_request_2)

    def test_get_receivers_for_support_message(self):
        self.superuser.profile.request_notification_enabled = True
        self.superuser.save()
        new_support = Support.objects.create(title="title",
                                             instance=self.test_instance,
                                             opened_by=self.standard_user)
        support_message = SupportMessage.objects.create(content="message content", sender=self.standard_user,
                                                        support=new_support)

        receivers = _get_receivers_for_support_message(support_message)
        self.assertCountEqual([self.superuser.email, self.superuser_2.email], receivers)

        support_message = SupportMessage.objects.create(content="message content admin", sender=self.superuser,
                                                        support=new_support)
        receivers = _get_receivers_for_support_message(support_message)
        self.assertCountEqual([self.standard_user.email, self.superuser_2.email], receivers)

    def test_get_receivers_for_request_message(self):
        self.superuser.profile.request_notification_enabled = True
        request_message = RequestMessage.objects.create(sender=self.standard_user, content="message content",
                                                        request=self.test_request)
        receivers = _get_receivers_for_request_message(request_message)
        self.assertCountEqual([self.superuser.email, self.superuser_2.email], receivers)
        request_message = RequestMessage.objects.create(sender=self.superuser, content="message content admin",
                                                        request=self.test_request)
        receivers = _get_receivers_for_request_message(request_message)
        self.assertCountEqual([self.standard_user.email, self.superuser_2.email], receivers)
