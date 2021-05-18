from collections import OrderedDict

from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import Instance
from service_catalog.serializers.instance_serializer import InstanceSerializer
from tests.base_test_request import BaseTestRequest


class TestInstanceList(BaseTestRequest):

    def setUp(self):
        super(TestInstanceList, self).setUp()
        self.url = reverse('api_admin_instance_list')

    def test_list_instance(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Instance.objects.all().count(), len(response.data))
        all_instances = Instance.objects.all()
        serializer = InstanceSerializer(all_instances, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_standard_user_cannot_list_instances(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
