from rest_framework.reverse import reverse

from tests.test_service_catalog.test_api.test_instance.test_spec.test_spec_put import TestApiSpecPut


class TestApiUserSpecPut(TestApiSpecPut):

    def setUp(self):
        super(TestApiUserSpecPut, self).setUp()
        self.target_spec = "user-spec"
        self.get_spec_details_url = reverse('api_instance_user_spec_details', kwargs=self.kwargs)

    def test_admin_put_user_spec(self):
        self.test_admin_put_spec()

    def test_cannot_put_user_spec_when_logout(self):
        self.test_cannot_put_spec_when_logout()
