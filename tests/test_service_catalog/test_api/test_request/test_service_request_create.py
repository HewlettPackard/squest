from collections import OrderedDict

from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import Request, Instance
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestApiServiceRequestListCreate(BaseTestRequest):

    def setUp(self):
        super(TestApiServiceRequestListCreate, self).setUp()
        self.kwargs = {
            "pk": self.service_test.id,
        }
        self.url = reverse('api_service_request_list_create', kwargs=self.kwargs)
        self.data = {
            'instance_name': 'instance test',
            'billing_group': None,
            'fill_in_survey': {
                'text_variable': 'my text'
            }
        }
        self.expected = {
            'instance_name': 'instance test',
            'billing_group': None,
            'fill_in_survey': OrderedDict([
                ('text_variable', 'my text')
            ])}

    def test_can_create(self):
        self._check_create()

    def test_can_create_without_billing_group_given(self):
        self.data.pop('billing_group')
        self._check_create()
        self.client.force_login(self.standard_user)
        self._check_create()

    def test_cannot_create_when_service_is_disabled(self):
        self.service_test.enabled = False
        self.service_test.save()
        self._check_create(status.HTTP_404_NOT_FOUND)

    def test_cannot_create_when_logout(self):
        self.client.logout()
        self._check_create(status.HTTP_403_FORBIDDEN)

    def test_cannot_create_on_non_existing_service(self):
        self.kwargs['pk'] = 9999999
        self.url = reverse('api_service_request_list_create', kwargs=self.kwargs)
        self._check_create(status.HTTP_404_NOT_FOUND)

    def test_cannot_create_with_non_own_billing_group(self):
        self.service_test.billing_group_is_selectable = True
        self.service_test.save()
        self.test_billing_group.user_set.add(self.superuser)
        self.data['billing_group'] = self.test_billing_group.id
        self.expected['billing_group'] = self.test_billing_group.id
        self._check_create()
        self.client.force_login(user=self.standard_user)
        self._check_create(status.HTTP_400_BAD_REQUEST)


    def test_cannot_create_with_non_existing_billing_group(self):
        self.service_test.billing_group_is_selectable = True
        self.service_test.billing_groups_are_restricted = False
        self.service_test.save()
        self.data['billing_group'] = 9999999
        self._check_create(status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_with_billing_group_different_from_the_imposed_one(self):
        self.service_test.billing_group_id = self.test_billing_group.id
        self.service_test.billing_groups_are_restricted = False
        self.service_test.save()
        self.data['billing_group'] = self.test_billing_group.id
        self.expected['billing_group'] = self.test_billing_group.id
        self._check_create()
        self.data['billing_group'] = self.test_billing_group2.id
        self._check_create()

    def test_cannot_create_with_wrong_survey_fields(self):
        self.data['fill_in_survey']['wrong_field_name'] = self.data['fill_in_survey'].pop('text_variable')
        self._check_create(status.HTTP_400_BAD_REQUEST)

    def _check_create(self, status_expected=None):
        response_status = status_expected
        offset = 0
        if status_expected is None:
            offset = 1
            response_status = status.HTTP_201_CREATED
        instance_count = Instance.objects.count()
        request_count = Request.objects.count()
        response = self.client.post(self.url, data=self.data, content_type="application/json")
        self.assertEqual(response.status_code, response_status)
        self.assertEqual(instance_count + offset, Instance.objects.count())
        self.assertEqual(request_count + offset, Request.objects.count())
        if status_expected is None:
            self.assertEqual(response.data, self.expected)
