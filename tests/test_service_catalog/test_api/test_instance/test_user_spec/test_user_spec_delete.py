from rest_framework.reverse import reverse

from tests.test_service_catalog.test_api.test_instance.test_spec.test_spec_delete import TestApiSpecDelete


class TestApiUserSpecDelete(TestApiSpecDelete):

    def setUp(self):
        super(TestApiUserSpecDelete, self).setUp()
        self.get_spec_create_url = reverse('api_instance_user_spec_details', kwargs=self.kwargs)
        self.target_spec = "user-spec"

    def test_admin_delete_user_spec(self):
        self.test_admin_delete_spec()


    def test_cannot_delete_user_spec_when_logout(self):
        self.test_cannot_delete_spec_when_logout()
