from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_views.base_test_request import BaseTestRequest


class TestInstanceUpdate(BaseTestRequest):

    def setUp(self):
        super(TestInstanceUpdate, self).setUp()
        self.url = reverse('api_admin_instance_details', args=[self.test_instance.id])

        self.update_data = {
            "name": "new_name",
            "spec": {
                "key1": "value1",
                "key2": "value2"
            }
        }

    def test_update_instance(self):
        response = self.client.put(self.url, data=self.update_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_instance.refresh_from_db()
        expected = {
                "key1": "value1",
                "key2": "value2"
            }
        self.assertDictEqual(self.test_instance.spec, expected)
        self.assertEqual(self.test_instance.name, "new_name")
