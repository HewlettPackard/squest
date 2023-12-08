from django.test import TestCase
from django.test.testcases import TransactionTestCase
from rest_framework.test import APITestCase

from profiles.models import Organization


class SetupOrgCommon(TransactionTestCase):

    def setUp(self):
        # Organization
        self.org1 = Organization.objects.create(name='Organization 1')
        self.org2 = Organization.objects.create(name='Organization 2')
        self.org3 = Organization.objects.create(name='Organization 3')

        print("SetupOrgCommon finished")

class SetupOrg(TestCase, SetupOrgCommon):
    pass


class SetupOrgAPI(APITestCase, SetupOrgCommon):
    pass
