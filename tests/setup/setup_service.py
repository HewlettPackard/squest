from django.test import TestCase
from rest_framework.test import APITestCase

from service_catalog.models import Service
from tests.setup import SetupDummyAWXCommon


class SetupServiceCommon(SetupDummyAWXCommon):

    def setUp(self):
        super().setUp()
        # Team
        self.service_1 = Service.objects.create(name="Service 1", description="Description of service 1")
        self.service_2 = Service.objects.create(name="Service 2", description="Description of service 2")

        print("SetupServiceCommon finished")

class SetupService(TestCase, SetupServiceCommon):
    pass


class SetupServiceAPI(APITestCase, SetupServiceCommon):
    pass
