from service_catalog.forms import FormUtils
from test_service_catalog.base_test_request import BaseTestRequest


class TestPortfolio(BaseTestRequest):

    def setUp(self):
        super(TestPortfolio, self).setUp()

    def test_bulk_set_permission_on_operation(self):
        self.service_test.parent_portfolio = self.portfolio_test_1
        self.service_test.save()
        self.service_test_2.parent_portfolio = self.portfolio_test_1
        self.service_test_2.save()

        for current_perm in self.service_test.operations.values_list("permission", flat=True):
            self.assertEqual(current_perm, FormUtils.get_default_permission_for_operation())
        for current_perm in self.service_test_2.operations.values_list("permission", flat=True):
            self.assertEqual(current_perm, FormUtils.get_default_permission_for_operation())

        # apply new perm
        self.portfolio_test_1.bulk_set_permission_on_operation(self.admin_operation)
        for current_perm in self.service_test.operations.values_list("permission", flat=True):
            self.assertEqual(current_perm, self.admin_operation.id)
        for current_perm in self.service_test_2.operations.values_list("permission", flat=True):
            self.assertEqual(current_perm, self.admin_operation.id)