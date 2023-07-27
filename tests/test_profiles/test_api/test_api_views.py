from rest_framework import status
from rest_framework.reverse import reverse

from profiles.models import Quota
from resource_tracker_v2.models import AttributeDefinition
from tests.test_profiles.base.base_test_profile import BaseTestProfileAPI


class TestQuotaAPIView(BaseTestProfileAPI):

    def setUp(self):
        super(TestQuotaAPIView, self).setUp()

        self._list_create_url = reverse('quota_org_list_create',  kwargs={"scope_id": self.test_org.id})
        self._details_url = reverse('quota_org_details', kwargs={"scope_id": self.test_org.id,
                                                                 "pk": self.test_quota_org.id})

    def test_list_quota(self):
        response = self.client.get(self._list_create_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], Quota.objects.filter(scope=self.test_org).count())
        for quota in response.json()['results']:
            self.assertTrue("id" in quota)
            self.assertTrue("attribute_definition" in quota)
            self.assertTrue("limit" in quota)

    def test_create_quota(self):
        data = {
            "attribute_definition": self.other_attribute.id,
            "limit": 20
        }
        response = self.client.post(self._list_create_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_quota(self):
        data = {
            "attribute_definition": self.cpu_attribute.id,
            "limit": 20
        }
        response = self.client.patch(self._details_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_quota_org.refresh_from_db()
        self.assertEqual(self.test_quota_org.limit, 20)

    def test_delete_quota(self):
        id_to_delete = self.test_quota_org.id
        data = {
            "attribute_definition": self.cpu_attribute.id,
            "limit": 20
        }
        self.assertTrue(Quota.objects.filter(id=id_to_delete).exists())
        response = self.client.delete(self._details_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Quota.objects.filter(id=id_to_delete).exists())
