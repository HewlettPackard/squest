from profiles.api.serializers import ScopeSerializer
from profiles.models import Organization, Team, Scope
from django.test.testcases import TransactionTestCase


class ScopeSerializerTests(TransactionTestCase):

    def setUp(self):
        super(ScopeSerializerTests, self).setUp()
        self.organization = Organization.objects.create(name="Org")
        self.team = Team.objects.create(org=self.organization, name="Team")

    def test_scope_serializer_with_org(self):
        serializer = ScopeSerializer(instance=Scope.objects.get(id=self.organization.pk))

        self.assertEqual(
            serializer.data["organization"],
            {'id': self.organization.id, 'name': self.organization.name}
        )

        self.assertEqual(serializer.data["team"], {})

    def test_scope_serializer_with_team(self):
        serializer = ScopeSerializer(instance=Scope.objects.get(id=self.team.pk))

        self.assertEqual(
            serializer.data["organization"],
            {'id': self.team.org.id, 'name': self.team.org.name}
        )

        self.assertEqual(serializer.data["team"], {'id': self.team.id, 'name': self.team.name})
