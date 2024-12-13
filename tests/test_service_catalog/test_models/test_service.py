from service_catalog.forms.form_utils import FormUtils
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestService(BaseTestRequest):

    def setUp(self):
        super(TestService, self).setUp()

    def test_bulk_set_permission_on_operation(self):
        for current_perm in self.service_test.operations.values_list("permission", flat=True):
            self.assertEqual(current_perm, FormUtils.get_default_permission_for_operation())

        # apply new perm
        self.service_test.bulk_set_permission_on_operation(self.admin_operation)
        for current_perm in self.service_test.operations.values_list("permission", flat=True):
            self.assertEqual(current_perm, self.admin_operation.id)