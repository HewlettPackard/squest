from django.test import TestCase
from rest_framework.test import APITestCase

from service_catalog.models import CustomLink
from tests.test_service_catalog.base_test_request import BaseTestRequestCommon

class BaseTestCustomLinkCommon(BaseTestRequestCommon):

    def setUp(self):
        super(BaseTestCustomLinkCommon, self).setUp()

        self.test_custom_link = CustomLink.objects.create(name="test_custom_link",
                                                          text="custom_link",
                                                          url="https://custom-link.domain")
        self.test_custom_link.services.set([self.service_test])

class BaseTestCustomLink(TestCase, BaseTestCustomLinkCommon):
    pass


class BaseTestCustomLinkAPI(APITestCase, BaseTestCustomLinkCommon):
    pass
