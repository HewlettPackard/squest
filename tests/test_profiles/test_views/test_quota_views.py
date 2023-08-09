from django.urls import reverse

from profiles.models import Quota
from resource_tracker_v2.models import AttributeDefinition
from tests.test_profiles.base.base_test_profile import BaseTestProfile


class TestQuotaViews(BaseTestProfile):

    def setUp(self):
        super(TestQuotaViews, self).setUp()
        args = {
            "scope_id": self.test_org.id
        }
        self.create_url = reverse('profiles:organization_quota_edit', kwargs=args)

    def test_quota_list(self):
        response = self.client.get(reverse('profiles:organization_details', kwargs={'pk': self.test_org.id}))
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["quotas"].data.data), Quota.objects.filter(scope=self.test_org).count())

    def test_quota_details(self):
        response = self.client.get(reverse('profiles:quota_details', kwargs={'quota_id': self.test_quota_org.id}))
        self.assertEqual(200, response.status_code)
        self.assertTrue("quotas_teams_consumption" in response.context)
        self.assertTrue("team_limit_table" in response.context)
        self.assertTrue("instance_consumption_table" in response.context)
        self.assertTrue("instances_consumption" in response.context)

    def test_quota_edit(self):
        # Get
        response = self.client.get(self.create_url)
        self.assertEqual(200, response.status_code)

        # Post
        data = {
            f"attribute_definition_{self.cpu_attribute.id}": 100,
            f"attribute_definition_{self.other_attribute.id}": 50
        }
        number_quota_before = Quota.objects.count()
        self.assertEqual(self.test_quota_org.limit, 150)
        response = self.client.post(self.create_url, data=data)
        self.assertEqual(302, response.status_code)
        self.test_quota_org.refresh_from_db()
        self.assertEqual(self.test_quota_org.limit, 100)
        self.assertEqual(number_quota_before + 1, Quota.objects.count())
