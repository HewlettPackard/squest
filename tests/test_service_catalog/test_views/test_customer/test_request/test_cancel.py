from django.core.exceptions import PermissionDenied
from django.urls import reverse

from service_catalog.models import Request, RequestState, InstanceState
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestCustomerRequestViewTest(BaseTestRequest):

    def setUp(self):
        super(TestCustomerRequestViewTest, self).setUp()

    def _assert_can_cancel(self):
        args = {
            'pk': self.test_request.id
        }
        url = reverse('service_catalog:request_cancel', kwargs=args)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual(0, Request.objects.filter(id=self.test_request.id).count())

    def _assert_cannot_cancel(self):
        args = {
            'pk': self.test_request.id
        }

        url = reverse('service_catalog:request_cancel', kwargs=args)
        self.client.post(url)
        self.assertRaises(PermissionDenied)

    def test_request_cancel_by_admin(self):
        self._assert_can_cancel()

    def test_request_cancel_by_other(self):
        self.client.login(username=self.standard_user_2, password=self.common_password)
        self._assert_cannot_cancel()

    def test_request_cannot_be_canceled_on_forbidden_states(self):
        self.test_instance.state = InstanceState.AVAILABLE
        self.test_instance.save()
        for state in [RequestState.FAILED, RequestState.COMPLETE, RequestState.PROCESSING]:
            print(f"{self.test_request.state} --> {state}")
            self.test_request.state = state
            self.test_request.save()
            self._assert_cannot_cancel()

    def test_admin_can_cancel_from_admin_view(self):
        args = {
            'pk': self.test_request.id
        }
        url = reverse('service_catalog:request_cancel', kwargs=args)
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual(0, Request.objects.filter(id=self.test_request.id).count())
