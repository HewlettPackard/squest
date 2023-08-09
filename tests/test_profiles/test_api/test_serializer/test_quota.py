from profiles.api.serializers import QuotaSerializer
from profiles.models import Organization, Team, Quota
from resource_tracker_v2.models import AttributeDefinition
from django.test.testcases import TransactionTestCase


class QuotaSerializerTests(TransactionTestCase):

    def setUp(self):
        super(QuotaSerializerTests, self).setUp()
        self.organization = Organization.objects.create(name="Org")
        self.team = Team.objects.create(org=self.organization, name="Team")
        self.attribute = AttributeDefinition.objects.create(name="attribute")

    def test_create_quota_on_org(self):
        self.assertEqual(Quota.objects.count(), 0)
        data = {
            "attribute_definition": self.attribute.id,
            "limit": 20,
            "scope": self.organization.id
        }

        serializer = QuotaSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(Quota.objects.count(), 1)

    def test_create_quota_on_team_fail(self):
        # Can not create quota on team if quota doesnt exist on org
        data = {
            "attribute_definition": self.attribute.id,
            "limit": 20,
            "scope": self.team.id
        }

        serializer = QuotaSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_create_quota_on_org_then_team(self):
        # Org quota
        self.assertEqual(Quota.objects.count(), 0)
        data = {
            "attribute_definition": self.attribute.id,
            "limit": 20,
            "scope": self.organization.id
        }

        serializer = QuotaSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(Quota.objects.count(), 1)

        # Team quota
        data = {
            "attribute_definition": self.attribute.id,
            "limit": 20,
            "scope": self.team.id
        }

        serializer = QuotaSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(Quota.objects.count(), 2)

    def test_create_quota_on_org_then_team_fail_org_limit_less_than_consumed(self):
        self.assertEqual(Quota.objects.count(), 0)

        # Org  attr = 20
        data = {
            "attribute_definition": self.attribute.id,
            "limit": 20,
            "scope": self.organization.id
        }
        serializer = QuotaSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(Quota.objects.count(), 1)

        # Team  attr = 20
        data = {
            "attribute_definition": self.attribute.id,
            "limit": 20,
            "scope": self.team.id
        }

        serializer = QuotaSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(Quota.objects.count(), 2)

        # Org  attr = 10 but team is still 20 so failed
        data = {
            "attribute_definition": self.attribute.id,
            "limit": 20,
            "scope": self.organization.id
        }
        serializer = QuotaSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(Quota.objects.count(), 2)

    def test_create_quota_on_org_then_team_fail_team_limit_more_than_available(self):
        self.assertEqual(Quota.objects.count(), 0)

        # Org  attr = 20
        data = {
            "attribute_definition": self.attribute.id,
            "limit": 20,
            "scope": self.organization.id
        }
        serializer = QuotaSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(Quota.objects.count(), 1)

        # Team  attr = 20
        data = {
            "attribute_definition": self.attribute.id,
            "limit": 20,
            "scope": self.team.id
        }

        serializer = QuotaSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(Quota.objects.count(), 2)

        # Team  attr = 21 but org is still 20 so failed
        data = {
            "attribute_definition": self.attribute.id,
            "limit": 21,
            "scope": self.team.id
        }
        serializer = QuotaSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(Quota.objects.count(), 2)

    def test_create_quota_on_org_limit_0(self):
        self.assertEqual(Quota.objects.count(), 0)
        data = {
            "attribute_definition": self.attribute.id,
            "limit": 0,
            "scope": self.organization.id
        }

        serializer = QuotaSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(Quota.objects.count(), 1)

    def test_create_quota_on_org_negative_limit(self):
        self.assertEqual(Quota.objects.count(), 0)
        data = {
            "attribute_definition": self.attribute.id,
            "limit": -1,
            "scope": self.organization.id
        }

        serializer = QuotaSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(Quota.objects.count(), 0)

    def test_create_quota_on_org_then_team_with_limit_0(self):
        # Org quota
        self.assertEqual(Quota.objects.count(), 0)
        data = {
            "attribute_definition": self.attribute.id,
            "limit": 20,
            "scope": self.organization.id
        }

        serializer = QuotaSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(Quota.objects.count(), 1)

        # Team quota
        data = {
            "attribute_definition": self.attribute.id,
            "limit": 0,
            "scope": self.team.id
        }

        serializer = QuotaSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(Quota.objects.count(), 2)

    def test_create_quota_on_org_then_team_with_negative_limit(self):
        # Org quota
        self.assertEqual(Quota.objects.count(), 0)
        data = {
            "attribute_definition": self.attribute.id,
            "limit": 20,
            "scope": self.organization.id
        }

        serializer = QuotaSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(Quota.objects.count(), 1)

        # Team quota
        data = {
            "attribute_definition": self.attribute.id,
            "limit": -1,
            "scope": self.team.id
        }

        serializer = QuotaSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(Quota.objects.count(), 1)
