from rest_framework.reverse import reverse

from tests.test_service_catalog.test_api.test_instance.test_spec.test_spec_create import TestApiSpecCreate


class TestApiUserSpecCreate(TestApiSpecCreate):

    def setUp(self):
        super(TestApiUserSpecCreate, self).setUp()
        self.target_spec = "user-spec"
        self.get_spec_details_url = reverse('api_instance_user_spec_details', kwargs=self.kwargs)

    def test_admin_create_user_spec(self):
        self.test_admin_create_spec()

    def test_customer_cannot_create_user_spec(self):
        self.test_customer_cannot_create_spec()

    def test_cannot_create_user_spec_when_logout(self):
        self.test_cannot_create_spec_when_logout()
