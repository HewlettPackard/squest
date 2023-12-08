from django.test import TestCase
from rest_framework.test import APITestCase

from service_catalog.models import Request
from tests.setup import SetupInstanceCommon


class SetupRequestCommon(SetupInstanceCommon):

    def setUp(self):
        super().setUp()
        # Org 1
        self.request_1_org1 = Request.objects.create(instance=self.instance_1_org1,
                                                     operation=self.operation_create_1)
        # Org 2 - Team 1
        self.request_2_team1org2 = Request.objects.create(instance=self.instance_2_team1org2,
                                                          operation=self.operation_create_1)
        self.request_3_team1org2 = Request.objects.create(instance=self.instance_3_team1org2,
                                                          operation=self.operation_create_1)
        # Org 2 - Team 2
        self.request_4_team2org2 = Request.objects.create(instance=self.instance_4_team2org2,
                                                          operation=self.operation_create_1)
        self.request_5_team2org2 = Request.objects.create(instance=self.instance_5_team2org2,
                                                          operation=self.operation_create_1)
        # Org 2
        self.request_6_org2 = Request.objects.create(instance=self.instance_6_org2,
                                                     operation=self.operation_create_1)
        # Org 3 - Team 1
        self.request_7_team1org3 = Request.objects.create(instance=self.instance_7_team1org3,
                                                          operation=self.operation_create_1)
        # Org 3
        self.request_8_org3 = Request.objects.create(instance=self.instance_8_org3
                                                     , operation=self.operation_create_1)
        print("SetupRequestCommon finished")


class SetupRequest(TestCase, SetupRequestCommon):
    pass


class SetupRequestAPI(APITestCase, SetupRequestCommon):
    pass
