from django.core.exceptions import ValidationError

from profiles.models import BillingGroup
from service_catalog.forms import ServiceRequestForm
from tests.test_service_catalog.base import BaseTest


class TestRequestForm(BaseTest):

    def setUp(self):
        super(TestRequestForm, self).setUp()
        self.service_test.billing_groups_are_restricted = True
        self.service_test.billing_group_is_selectable = True
        self.service_test.billing_group_is_shown = True
        self.service_test.billing_group_id = None
        self.service_test.save()

    def test_cannot_create_request_without_billing_group_on_restricted_billing(self):
        parameters = {
            'service_id': self.service_test.id,
            'operation_id': self.create_operation_test.id
        }
        data = {
            "squest_instance_name": "instance test",
            "text_variable": "text"
        }
        form = ServiceRequestForm(self.standard_user, data, **parameters)
        self.assertRaises(ValidationError, form.clean_billing_group_id)

    def test_create_request_with_billing_group_on_restricted_billing(self):
        self.test_billing_group.user_set.add(self.standard_user)
        parameters = {
            'service_id': self.service_test.id,
            'operation_id': self.create_operation_test.id
        }
        instance_name = "instance test"
        text_var = "text"
        data = {
            "squest_instance_name": instance_name,
            "billing_group_id": self.test_billing_group.id,
            "text_variable": text_var
        }
        form = ServiceRequestForm(self.standard_user, data, **parameters)
        self.assertEqual([(self.test_billing_group.id, self.test_billing_group.name)], form.fields['billing_group_id'].choices)
        self.assertTrue(form.is_valid())
        request = form.save()
        self.assertEqual(request.instance.name, instance_name)
        self.assertEqual(request.instance.billing_group_id, self.test_billing_group.id)
        self.assertEqual(request.fill_in_survey["text_variable"], text_var)

    def test_create_request_with_non_owned_billing_group_on_restricted_billing(self):
        parameters = {
            'service_id': self.service_test.id,
            'operation_id': self.create_operation_test.id
        }
        instance_name = "instance test"
        text_var = "text"
        data = {
            "squest_instance_name": instance_name,
            "billing_group_id": self.test_billing_group.id,
            "text_variable": text_var
        }
        form = ServiceRequestForm(self.standard_user, data, **parameters)
        self.assertEqual([], form.fields['billing_group_id'].choices)
        self.assertFalse(form.is_valid())

    def test_create_request_with_billing_group_on_non_restricted_billing(self):
        self.service_test.billing_groups_are_restricted = False
        self.service_test.save()
        parameters = {
            'service_id': self.service_test.id,
            'operation_id': self.create_operation_test.id
        }
        data = {
            "squest_instance_name": "instance test",
            "billing_group_id": self.test_billing_group.id,
            "text_variable": "text"
        }
        form = ServiceRequestForm(self.standard_user, data, **parameters)
        self.assertEqual([(billing_group.id, billing_group.name) for billing_group in BillingGroup.objects.all()], form.fields['billing_group_id'].choices)
        self.assertTrue(form.is_valid())
