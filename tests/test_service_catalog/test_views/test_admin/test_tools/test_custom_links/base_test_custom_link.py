from service_catalog.models import CustomLink
from tests.test_service_catalog.base_test_request import BaseTestRequest


class BaseTestCustomLink(BaseTestRequest):

    def setUp(self):
        super(BaseTestCustomLink, self).setUp()

        self.test_custom_link = CustomLink.objects.create(name="test_custom_link",
                                                          text="custom_link",
                                                          url="https://custom-link.domain")
        self.test_custom_link.services.set([self.service_test])
