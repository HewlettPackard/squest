from django.test import TestCase
from rest_framework.test import APITestCase

from profiles.models import Team
from tests.setup import SetupOrgCommon


class SetupTeamCommon(SetupOrgCommon):

    def setUp(self):
        super().setUp()
        # Team
        self.team1org2 = Team.objects.create(name='Org2 - Team 1', org=self.org2)
        self.team2org2 = Team.objects.create(name='Org2 - Team 2', org=self.org2)
        self.team1org3 = Team.objects.create(name='Org3 - Team 1', org=self.org3)
        print("SetupTeamCommon finished")


class SetupTeam(TestCase, SetupTeamCommon):
    pass


class SetupTeamAPI(APITestCase, SetupTeamCommon):
    pass
