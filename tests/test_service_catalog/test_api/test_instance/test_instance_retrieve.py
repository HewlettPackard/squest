from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestInstanceRetrieve(BaseTestRequestAPI):

    def setUp(self):
        super(TestInstanceRetrieve, self).setUp()
        self.url = reverse('api_instance_details', args=[self.test_instance.id])

    def _assert_can_get_details(self, response, is_admin=True):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("id" in response.json())
        self.assertTrue("name" in response.json())
        self.assertTrue("state" in response.json())
        self.assertTrue("quota_scope" in response.json())
        self.assertTrue("service" in response.json())
        self.assertTrue("user_spec" in response.json())
        if is_admin:
            self.assertTrue("spec" in response.json())
        else:
            self.assertFalse("spec" in response.json())
        self.assertTrue("resources" in response.json())
        self.assertEqual(response.data['id'], self.test_instance.id)
        self.assertEqual(response.data['name'], self.test_instance.name)
        self.assertEqual(response.data['user_spec'], self.test_instance.user_spec)
        if is_admin:
            self.assertEqual(response.data['spec'], self.test_instance.spec)
        self.assertEqual(response.data['state'], self.test_instance.state)
        self.assertEqual(response.data['service'], self.test_instance.service.id)
        self.assertEqual(response.data['requester'].get('id'), self.test_instance.requester.id)
        self.assertEqual(response.data['quota_scope']["id"], self.test_instance.quota_scope.id)

    def test_get_details_as_admin(self):
        response = self.client.get(self.url, format='json')
        self._assert_can_get_details(response)


    def test_cannot_retrieve_instance_details_when_logout(self):
        self.client.logout()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
