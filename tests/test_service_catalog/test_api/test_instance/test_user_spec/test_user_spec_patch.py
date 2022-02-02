from rest_framework.reverse import reverse

from tests.test_service_catalog.test_api.test_instance.test_spec.test_spec_patch import TestApiSpecPatch


class TestApiUserSpecPatch(TestApiSpecPatch):

    def setUp(self):
        super(TestApiUserSpecPatch, self).setUp()
        self.get_spec_details_url = reverse('api_instance_user_spec_details', kwargs=self.kwargs)
        self.target_spec = "user-spec"
        self.expected_data = self.expected_user_spec

    def test_admin_patch_user_spec(self):
        self.test_admin_patch_spec()

    def test_customer_cannot_patch_user_spec(self):
        self.test_customer_cannot_patch_spec()

    def test_cannot_patch_user_spec_when_logout(self):
        self.test_cannot_patch_spec_when_logout()
