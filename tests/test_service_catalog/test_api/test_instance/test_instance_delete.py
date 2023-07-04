from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_204_NO_CONTENT
from rest_framework.reverse import reverse

from service_catalog.models import Instance
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestInstanceDelete(BaseTestRequest):

    def setUp(self):
        super(TestInstanceDelete, self).setUp()
        self.url = reverse('api_instance_details', args=[self.test_instance.id])

    def test_admin_can_delete_instance(self):
        old_instance_count = Instance.objects.count()
        response = self.client.delete(self.url)
        new_instance_count = Instance.objects.count()
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(old_instance_count - 1, new_instance_count)

    def test_cannot_delete_instance_when_logout(self):
        self.client.logout()
        old_instance_count = Instance.objects.count()
        response = self.client.delete(self.url)
        new_instance_count = Instance.objects.count()
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
        self.assertEqual(old_instance_count, new_instance_count)
