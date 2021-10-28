from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestInstance(BaseTestRequest):

    def setUp(self):
        super(TestInstance, self).setUp()

    def test_update_permission_when_change_spoc(self):
        first_spoc = self.test_instance.spoc
        self.assertTrue(first_spoc.has_perm('change_instance', self.test_instance))
        self.assertTrue(first_spoc.has_perm('view_instance', self.test_instance))
        self.assertFalse(self.standard_user_2.has_perm('change_instance', self.test_instance))
        self.assertFalse(self.standard_user_2.has_perm('view_instance', self.test_instance))
        self.test_instance.spoc = self.standard_user_2
        self.test_instance.save()
        self.assertFalse(first_spoc.has_perm('change_instance', self.test_instance))
        self.assertFalse(first_spoc.has_perm('view_instance', self.test_instance))
        self.assertTrue(self.standard_user_2.has_perm('change_instance', self.test_instance))
        self.assertTrue(self.standard_user_2.has_perm('view_instance', self.test_instance))
