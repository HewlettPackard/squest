from profiles.models import Quota
from resource_tracker_v2.models import Resource
from tests.test_profiles.base.base_test_profile import BaseTestProfile


class TestQuota(BaseTestProfile):

    def setUp(self):
        super(TestQuota, self).setUp()

        self.test_instance.quota_scope = self.team1
        self.test_instance.save()
        self.resource_server.service_catalog_instance = self.test_instance
        self.resource_server.save()

    def _add_resource_on_instance(self, instance):
        new_resource = Resource.objects.create(name=f"new_resource{instance.id}",
                                               resource_group=self.rg_physical_servers)
        new_resource.set_attribute(self.cpu_attribute, 10)
        new_resource.service_catalog_instance = instance
        new_resource.save()
        return new_resource

    def test_consumed_from_team(self):
        # get the consumption with one resource
        self.assertEqual(self.test_quota_team.consumed, 12)

        # add a new resource
        self._add_resource_on_instance(self.test_instance)

        self.assertEqual(self.test_quota_team.consumed, 22)

    def test_get_available_from_team(self):
        self.assertEqual(self.test_quota_team.available, 88)

    def test_get_available_from_org(self):
        # org has 150 in limit total with one team with limit 100
        self.assertEqual(self.test_quota_org.available, 50)

    def test_consumed_from_org(self):
        self.assertEqual(self.test_quota_org.consumed, 100)

        # add a resource to the org level (not in team)
        self._add_resource_on_instance(self.test_instance_2)
        self.test_instance_2.quota_scope = self.test_org
        self.test_instance_2.save()
        self.assertEqual(self.test_quota_org.consumed, 110)

        # add a resource in the team (the org consumption should not move)
        self.assertEqual(self.test_quota_team.consumed, 12)
        self._add_resource_on_instance(self.test_instance_3)
        self.test_instance_3.quota_scope = self.team1
        self.test_instance_3.save()
        self.assertEqual(self.test_quota_org.consumed, 110)
        self.assertEqual(self.test_quota_team.consumed, 22)


    def test_post_delete_team_quota(self):

        self.assertTrue(Quota.objects.filter(id=self.test_quota_team.id).exists())
        self.assertTrue(Quota.objects.filter(id=self.test_quota_org.id).exists())

        self.test_quota_org.delete()

        self.assertFalse(Quota.objects.filter(id=self.test_quota_team.id).exists())
        self.assertFalse(Quota.objects.filter(id=self.test_quota_org.id).exists())
