from django.urls import reverse

from service_catalog.models import Operation, Service
from tests.base import BaseTest


class ServiceDeleteTestCase(BaseTest):

    def setUp(self):
        super(ServiceDeleteTestCase, self).setUp()
        args = {
            "service_id": self.service_test.id
        }
        self.url = reverse('edit_service', kwargs=args)
        self.data = {
            "name": "service-test-updated",
            "description": "description-of-service-test-updated"
        }

    def test_admin_can_edit_service(self):
        response = self.client.post(self.url, data=self.data)
        self.assertEquals(302, response.status_code)
        self.service_test.refresh_from_db()
        self.assertEquals(self.service_test.name, "service-test-updated")
        self.assertEquals(self.service_test.description, "description-of-service-test-updated")

    def test_standard_user_cannot_edit_service(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        response = self.client.post(self.url, data=self.data)
        self.assertEquals(302, response.status_code)
        self.service_test.refresh_from_db()
        self.assertEquals(self.service_test.name, "service-test")
        self.assertEquals(self.service_test.description, "description-of-service-test")
