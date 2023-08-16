from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import Instance
from service_catalog.api.serializers import InstanceReadSerializer
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestInstanceList(BaseTestRequestAPI):

    def setUp(self):
        super(TestInstanceList, self).setUp()
        self.url = reverse('api_instance_list')

    def test_list_instance(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Instance.objects.all().count(), response.data['count'])
        all_instances = Instance.objects.all()
        serializer = InstanceReadSerializer(all_instances, many=True)
        self.assertEqual(response.data['results'], serializer.data)

    def test_standard_user_can_list_his_own_instances(self):
        self.client.force_login(self.standard_user)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data['count'],
            Instance.get_queryset_for_user(self.standard_user, 'service_catalog.view_instance').count()
        )
        instance_id_list = [request['id'] for request in response.data['results']].sort()
        instance_id_list_db = [instance.id for instance in
                               Instance.get_queryset_for_user(self.standard_user, 'service_catalog.view_instance')].sort()
        self.assertEqual(instance_id_list, instance_id_list_db)

    def test_cannot_get_instance_list_when_logout(self):
        self.client.logout()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
