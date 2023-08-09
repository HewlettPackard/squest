from rest_framework import status
from rest_framework.reverse import reverse

from profiles.models import Quota
from tests.test_profiles.base.base_test_profile import BaseTestProfileAPI


class TestQuotaAPIView(BaseTestProfileAPI):

    def setUp(self):
        super(TestQuotaAPIView, self).setUp()

        self._list_create_url = reverse('api_quota_list')
        self._details_url = reverse('api_quota_details', kwargs={"pk": self.test_quota_org.id})

    def test_list_quota(self):
        response = self.client.get(f"{self._list_create_url}?scope={self.test_org.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], Quota.objects.filter(scope=self.test_org).count())
        for quota in response.json()['results']:
            self.assertTrue("id" in quota)
            self.assertTrue("attribute_definition" in quota)
            self.assertTrue("limit" in quota)

    def test_create_quota(self):
        data = {
            "attribute_definition": self.other_attribute.id,
            "limit": 20,
            "scope": self.test_quota_org.id
        }
        response = self.client.post(self._list_create_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_quota(self):
        data = {
            "attribute_definition": self.cpu_attribute.id,
            "limit": 20,
            "scope": self.test_quota_org.id
        }
        response = self.client.patch(self._details_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_quota_org.refresh_from_db()
        self.assertEqual(self.test_quota_org.limit, 20)

    def test_delete_quota(self):
        id_to_delete = self.test_quota_org.id
        id_team_deleted_by_post_delete = self.test_quota_team.id
        self.assertTrue(Quota.objects.filter(id=id_to_delete).exists())
        self.assertTrue(Quota.objects.filter(id=id_team_deleted_by_post_delete).exists())
        response = self.client.delete(self._details_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Quota.objects.filter(id=id_to_delete).exists())
        self.assertFalse(Quota.objects.filter(id=id_team_deleted_by_post_delete).exists())
