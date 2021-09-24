from django.core.exceptions import PermissionDenied
from django.urls import reverse

from service_catalog.models import Request
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestCustomerRequestViewTest(BaseTestRequest):

    def setUp(self):
        super(TestCustomerRequestViewTest, self).setUp()

    def _assert_can_cancel(self):
        args = {
            'request_id': self.test_request.id
        }
        url = reverse('service_catalog:customer_request_cancel', kwargs=args)
        response = self.client.post(url)
        self.assertEquals(302, response.status_code)
        self.assertEquals(0, Request.objects.filter(id=self.test_request.id).count())

    def _assert_cannot_cancel(self):
        args = {
            'request_id': self.test_request.id
        }
        url = reverse('service_catalog:customer_request_cancel', kwargs=args)
        self.client.post(url)
        self.assertRaises(PermissionDenied)

    def test_request_cancel_by_admin(self):
        self._assert_can_cancel()

    def test_request_cancel_by_owner(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        self._assert_can_cancel()

    def test_request_cancel_by_other(self):
        self.client.login(username=self.standard_user_2, password=self.common_password)
        self._assert_cannot_cancel()

    def test_request_cannot_be_canceled_once_accepted(self):
        for state in ["ACCEPTED", "FAILED", "COMPLETE", "PROCESSING"]:
            self.test_request.state = state
            self._assert_cannot_cancel()

    def test_admin_can_cancel_from_admin_view(self):
        args = {
            'request_id': self.test_request.id
        }
        url = reverse('service_catalog:admin_request_cancel', kwargs=args)
        response = self.client.post(url)
        self.assertEquals(302, response.status_code)
        self.assertEquals(0, Request.objects.filter(id=self.test_request.id).count())
