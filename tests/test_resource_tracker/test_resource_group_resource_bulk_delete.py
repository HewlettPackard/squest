from unittest import mock

from django.urls import reverse

from profiles.models import BillingGroup
from resource_tracker.models import Resource
from service_catalog.models import Instance
from tests.test_resource_tracker.base_test_resource_tracker import BaseTestResourceTracker


class ResourceGroupResourceBulkDeleteTest(BaseTestResourceTracker):
    def setUp(self):
        super(ResourceGroupResourceBulkDeleteTest, self).setUp()
        self.resource_to_delete_list = list()
        for x in range(5):
            instance = None
            if x == 2:
                billing_group = BillingGroup.objects.create(name=f"test_billing_bulk_delete_{x}")
                instance = Instance.objects.create(name=f"test_instance_bulk_delete_{x}",
                                                   service=self.service_test,
                                                   spoc=self.standard_user,
                                                   billing_group=billing_group)
            self.resource_to_delete_list.append(
                Resource.objects.create(name=f"test_bulk_delete_{x}", resource_group=self.rg_physical_servers,
                                        service_catalog_instance=instance).id
            )
        self.data = {"selection": self.resource_to_delete_list}
        self.url_confirm = reverse('resource_tracker:resource_group_resource_bulk_delete_confirm', kwargs={'resource_group_id': self.rg_physical_servers.id})
        self.url_delete = reverse('resource_tracker:resource_group_resource_bulk_delete', kwargs={'resource_group_id': self.rg_physical_servers.id})

    def test_admin_can_confirm_bulk_delete(self):
        response = self.client.post(self.url_confirm, data=self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set([resource.id for resource in response.context['object_list']]),
            set(self.resource_to_delete_list)
        )

    def test_admin_get_message_on_confirm_bulk_delete_with_empty_data(self):
        response = self.client.post(self.url_confirm)
        self.assertEqual(response.status_code, 302)

    def test_user_cannot_confirm_bulk_delete(self):
        self.client.force_login(self.standard_user)
        response = self.client.post(self.url_confirm, data=self.data)
        self.assertEqual(response.status_code, 302)

    def test_cannot_confirm_bulk_delete_when_logout(self):
        self.client.logout()
        response = self.client.post(self.url_confirm, data=self.data)
        self.assertEqual(response.status_code, 302)

    def test_admin_can_bulk_delete(self):
        with mock.patch("service_catalog.tasks.async_resource_attribute_quota_bindings_update_consumed.delay") as mock_quota:
            count = 0
            for resource_id in self.resource_to_delete_list:
                count += Resource.objects.get(id=resource_id).attributes.count()
            self.assertEqual(Resource.objects.filter(id__in=self.resource_to_delete_list).count(), 5)
            response = self.client.post(self.url_delete, data=self.data)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(mock_quota.call_count, count)
            self.assertEqual(Resource.objects.filter(id__in=self.resource_to_delete_list).count(), 0)

    def test_admin_get_message_on_bulk_delete_with_empty_data(self):
        response = self.client.post(self.url_delete)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Resource.objects.filter(id__in=self.resource_to_delete_list).count(), 5)

    def test_user_cannot_bulk_delete(self):
        self.client.force_login(self.standard_user)
        response = self.client.post(self.url_delete, data=self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Resource.objects.filter(id__in=self.resource_to_delete_list).count(), 5)

    def test_cannot_bulk_delete_when_logout(self):
        self.client.logout()
        response = self.client.post(self.url_delete, data=self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Resource.objects.filter(id__in=self.resource_to_delete_list).count(), 5)
