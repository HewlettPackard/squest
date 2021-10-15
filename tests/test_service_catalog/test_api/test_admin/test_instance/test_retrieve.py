from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestInstanceRetrieve(BaseTestRequest):

    def setUp(self):
        super(TestInstanceRetrieve, self).setUp()
        self.url = reverse('api_admin_instance_details', args=[self.test_instance.id])

    def test_get_details(self):
        response = self.client.get(self.url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("id" in response.json())
        self.assertTrue("name" in response.json())
        self.assertTrue("spec" in response.json())
        self.assertTrue("state" in response.json())
        self.assertTrue("billing_group" in response.json())
        self.assertTrue("service" in response.json())
        self.assertTrue("spec" in response.json())
        self.assertTrue("resources" in response.json())
        self.assertEqual(response.data['id'], self.test_instance.id)
        self.assertEqual(response.data['name'], self.test_instance.name)
        self.assertEqual(response.data['spec'], self.test_instance.spec)
        self.assertEqual(response.data['state'], self.test_instance.state)
        self.assertEqual(response.data['service'], self.test_instance.service.id)
        self.assertEqual(response.data['spoc'], self.test_instance.spoc.id)
        self.assertEqual(response.data['billing_group'], self.test_instance.billing_group)
        self.assertEqual(response.data['resources'],  list(self.test_instance.resources.all()))

    def test_standard_user_cannot_get_details(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
