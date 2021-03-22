from collections import OrderedDict

from rest_framework import status
from rest_framework.reverse import reverse

from tests.test_views.base_test_request import BaseTestRequest


class TestInstanceRetrieve(BaseTestRequest):

    def setUp(self):
        super(TestInstanceRetrieve, self).setUp()
        self.url = reverse('api_admin_instance_details', args=[self.test_instance.id])

    def test_get_details(self):
        response = self.client.get(self.url, format='json')

        expected_response = OrderedDict([('id', 1),
                                         ('name', 'test_instance_1'),
                                         ('spec', {}),
                                         ('state', 'PENDING'),
                                         ('service', 1)])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(expected_response, response.json())

    def test_standard_user_cannot_get_details(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
