from django.test import TestCase
from rest_framework.test import APITestCase

from service_catalog.models import Instance
from tests.setup import SetupOperationCommon, SetupTeamCommon


class SetupInstanceCommon(SetupOperationCommon, SetupTeamCommon):

    def setUp(self):
        SetupOperationCommon.setUp(self)
        SetupTeamCommon.setUp(self)

        # Org 1
        self.instance_1_org1 = Instance.objects.create(name="Instance 1 - Org 1",
                                                       quota_scope=self.org1,
                                                       service=self.service_1)
        # Org 2 - Team 1
        self.instance_2_team1org2 = Instance.objects.create(name="Instance 2 - Org 2 - Team 1",
                                                            quota_scope=self.team1org2,
                                                            service=self.service_1)
        self.instance_3_team1org2 = Instance.objects.create(name="Instance 3 - Org 2 - Team 1",
                                                            quota_scope=self.team1org2,
                                                            service=self.service_1)
        # Org 2 - Team 2
        self.instance_4_team2org2 = Instance.objects.create(name="Instance 4 - Org 2 - Team 2",
                                                            quota_scope=self.team2org2,
                                                            service=self.service_1)
        self.instance_5_team2org2 = Instance.objects.create(name="Instance 5 - Org 2 - Team 2",
                                                            quota_scope=self.team2org2,
                                                            service=self.service_1)
        # Org 2
        self.instance_6_org2 = Instance.objects.create(name="Instance 6 - Org 2 ",
                                                       quota_scope=self.org2,
                                                       service=self.service_1)
        # Org 3 - Team 1
        self.instance_7_team1org3 = Instance.objects.create(name="Instance 7 - Org 3 - Team 1",
                                                            quota_scope=self.team1org3,
                                                            service=self.service_1)
        # Org 3
        self.instance_8_org3 = Instance.objects.create(name="Instance 7 - Org 3",
                                                       quota_scope=self.org3,
                                                       service=self.service_1)

        print("SetupInstanceCommon finished")

class SetupInstance(TestCase, SetupInstanceCommon):
    pass


class SetupInstanceAPI(APITestCase, SetupInstanceCommon):
    pass
