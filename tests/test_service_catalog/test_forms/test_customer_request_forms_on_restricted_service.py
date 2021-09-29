from django.core.exceptions import ValidationError

from profiles.models import BillingGroup
from service_catalog.forms import ServiceRequestForm
from tests.test_service_catalog.base import BaseTest


class TestRequestForm(BaseTest):

    def setUp(self):
        super(TestRequestForm, self).setUp()
        self.billing_group_test = BillingGroup.objects.create(name="test")
        self.service_test.billing_groups_are_restricted = True
        self.service_test.billing_group_is_selectable = True
        self.service_test.billing_group_is_shown = True
        self.service_test.billing_group_id = None
        self.service_test.save()

    def test_create_request_without_billing_group_on_restricted_billing(self):
        parameters = {
            'service_id': self.service_test.id
        }
        data = {
            "instance_name": "instance test",
            "text_variable": "text"
        }
        form = ServiceRequestForm(self.standard_user, data, **parameters)
        self.assertRaises(ValidationError, form.clean_billing_group_id)

    def test_create_request_with_billing_group_on_restricted_billing(self):
        self.billing_group_test.user_set.add(self.standard_user)
        parameters = {
            'service_id': self.service_test.id
        }
        data = {
            "instance_name": "instance test",
            "billing_group_id": self.billing_group_test.id,
            "text_variable": "text"
        }
        form = ServiceRequestForm(self.standard_user, data, **parameters)
        self.assertEqual([(self.billing_group_test.id, self.billing_group_test.name)], form.fields['billing_group_id'].choices)
        self.assertTrue(form.is_valid())

    def test_create_request_with_billing_group_on_non_restricted_billing(self):
        self.service_test.billing_groups_are_restricted = False
        self.service_test.save()
        parameters = {
            'service_id': self.service_test.id
        }
        data = {
            "instance_name": "instance test",
            "billing_group_id": self.billing_group_test.id,
            "text_variable": "text"
        }
        form = ServiceRequestForm(self.standard_user, data, **parameters)
        self.assertEqual([(self.billing_group_test.id, self.billing_group_test.name)], form.fields['billing_group_id'].choices)
        self.assertTrue(form.is_valid())
