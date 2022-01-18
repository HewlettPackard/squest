from service_catalog.mail_utils import _get_admin_emails, _get_subject, _get_headers, \
    _get_receivers_for_request_message, _get_receivers_for_support_message

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
        self.test_instance = Instance.objects.create(name="test_instance_1", service=self.service_test,
                                                     spoc=self.standard_user)
        self.test_instance_2 = Instance.objects.create(name="test_instance_2", service=self.service_test,
                                                       spoc=self.standard_user)
        self.test_request = Request.objects.create(fill_in_survey=data,
                                                   instance=self.test_instance,
                                                   operation=self.create_operation_test,
                                                   user=self.standard_user)
        self.test_request_2 = Request.objects.create(fill_in_survey=data,
                                                   instance=self.test_instance_2,
                                                   operation=self.create_operation_test,
                                                   user=self.standard_user)

    def test_get_admin_emails(self):
        # Test 1 - admin disabled notification
        self.superuser.profile.notification_enabled = False
        self.superuser.save()
        self.assertEquals(0, len(_get_admin_emails(service=self.service_test)))

        # Test 2 - admin enabled notification but no service subscribed
        self.superuser.profile.notification_enabled = True
        self.superuser.save()
        self.assertEquals(0, len(_get_admin_emails(service=self.service_test)))

        # Test 3 - admin enabled notification and service subscribed
        self.superuser.profile.notification_enabled = True
        self.superuser.profile.subscribed_services_notification.add(self.service_test)
        self.superuser.save()
        self.assertEquals(1, len(_get_admin_emails(service=self.service_test)))

    def test_get_headers(self):
        excepted_list = ["Message-ID", "In-Reply-To", "References"]
        subject = _get_subject(self.test_instance)
        headers = _get_headers(subject)
        subject = _get_subject(self.test_instance_2)
        headers_2 = _get_headers(subject)
        for excepted_key in excepted_list:
            self.assertIn(excepted_key, headers)
            self.assertNotEqual(headers[excepted_key], headers_2[excepted_key])

    def test_get_subject(self):
        subject_instance = _get_subject(self.test_instance)
        subject_instance_2 = _get_subject(self.test_instance_2)
        self.assertNotEqual(subject_instance, subject_instance_2)
        subject_request = _get_subject(self.test_request)
        subject_request_2 = _get_subject(self.test_request_2)
        self.assertNotEqual(subject_request, subject_request_2)

    def test_get_receivers_for_support_message(self):
        self.superuser.profile.notification_enabled = True
        self.superuser.profile.subscribed_services_notification.add(self.service_test)
        new_support = Support.objects.create(title="title",
                                             instance=self.test_instance,
                                             opened_by=self.standard_user)
        support_message = SupportMessage.objects.create(content="message content", sender=self.standard_user,
                                                        support=new_support)
        receivers = _get_receivers_for_support_message(support_message)
        self.assertIn(self.superuser.email, receivers)
        self.assertNotIn(self.standard_user.email, receivers)
        support_message = SupportMessage.objects.create(content="message content admin", sender=self.superuser,
                                                        support=new_support)
        receivers = _get_receivers_for_support_message(support_message)
        self.assertIn(self.standard_user.email, receivers)
        self.assertNotIn(self.superuser.email, receivers)

    def test_get_receivers_for_request_message(self):
        self.superuser.profile.notification_enabled = True
        self.superuser.profile.subscribed_services_notification.add(self.service_test)
        request_message = RequestMessage.objects.create(sender=self.standard_user, content="message content",
                                                        request=self.test_request)
        receivers = _get_receivers_for_request_message(request_message)
        self.assertIn(self.superuser.email, receivers)
        self.assertNotIn(self.standard_user.email, receivers)
        request_message = RequestMessage.objects.create(sender=self.superuser, content="message content admin",
                                                        request=self.test_request)
        receivers = _get_receivers_for_request_message(request_message)
        self.assertIn(self.standard_user.email, receivers)
        self.assertNotIn(self.superuser.email, receivers)
