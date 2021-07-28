from django.urls import reverse

from profiles.models import BillingGroup
from service_catalog.forms import ServiceForm, EditServiceForm
from tests.base import BaseTest


class TestServiceForm(BaseTest):

    def setUp(self):
        super(TestServiceForm, self).setUp()
        self.billing_group_1 = BillingGroup.objects.create(name="first")
        self.data_list = [
            {
                "name": "new_service",
                "description": "a new service",
                "job_template": self.job_template_test.id,
                "billing": "defined",
                "billing_group_id": "",
                "billing_group_is_shown": "on"
            },
            {
                "name": "new_service_2",
                "description": "a new service 2",
                "job_template": self.job_template_test.id,
                "billing": "all_billing_groups",
                "billing_group_id": "",
                "billing_group_is_shown": "on"

            },
            {
                "name": "new_service_3",
                "description": "a new service 3",
                "job_template": self.job_template_test.id,
                "billing": "defined",
                "billing_group_id": self.billing_group_1.id

            },
            {
                "name": "new_service_4",
                "description": "a new service 4",
                "job_template": self.job_template_test.id,
                "billing": "defined",
                "billing_group_id": self.billing_group_1.id + 1

            },
            {
                "name": "new_service_5",
                "description": "a new service 5",
                "job_template": self.job_template_test.id,
                "billing": "restricted_billing_groups",
                "billing_group_id": "",
                "billing_group_is_shown": "on"
            },
        ]
        self.failed_expected = ["new_service_4"]

    def test_create_service(self):
        for data in self.data_list:
            form = ServiceForm(data)
            if form.is_valid():
                new_service = form.save()
                test_list = self.get_test_list(data, new_service)
                for test in test_list:
                    self.assertEquals(test['value'], test['expected'])
            else:
                self.assertIn(data['name'], self.failed_expected)

    def test_edit_service(self):
        for data in self.data_list:
            form = EditServiceForm(data, instance=self.service_test)
            if form.is_valid():
                form.save()
                test_list = self.get_test_list(data, self.service_test)
                for test in test_list:
                    self.assertEquals(test['value'], test['expected'])
            else:
                self.assertIn(data['name'], self.failed_expected)

    @staticmethod
    def get_test_list(data, service):
        is_selectable = data['billing'] == 'restricted_billing_groups' or data['billing'] == 'all_billing_groups'
        return [
            {
                'name': "name",
                'value': service.name,
                'expected': data['name']
            },
            {
                'name': "description",
                'value': service.description,
                'expected': data['description']
            },
            {
                'name': "billing_group_id",
                'value': service.billing_group_id,
                'expected': data['billing_group_id'] if data['billing_group_id'] != "" else None
            },
            {
                'name': "billing_group_is_shown",
                'value': service.billing_group_is_shown,
                'expected': data['billing_group_is_shown'] == "on" if 'billing_group_is_shown' in data.keys() else is_selectable
            },
            {
                'name': "billing_group_is_selectable",
                'value': service.billing_group_is_selectable,
                'expected': is_selectable
            },
            {
                'name': "billing_groups_are_restricted",
                'value': service.billing_groups_are_restricted,
                'expected': data['billing'] == 'restricted_billing_groups'
            },
        ]
