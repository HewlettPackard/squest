from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint
from service_catalog.forms.form_utils import FormUtils


class TestServiceCatalogOperationPermissionsViews(BaseTestRequest, TestPermissionEndpoint):
    def test_operation_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:operation_list',
                perm_str_list=['service_catalog.list_operation']
            ),
            TestingGetContextView(
                url='service_catalog:create_operation_list',
                perm_str_list=['service_catalog.list_operation'],
                url_kwargs={'service_id': self.create_operation_test.service.id}
            ),
            TestingGetContextView(
                url='service_catalog:operation_create',
                perm_str_list=['service_catalog.add_operation'],
            ),
            TestingPostContextView(
                url='service_catalog:operation_create',
                perm_str_list=['service_catalog.add_operation'],
                data={
                    'service': self.service_test.id,
                    'name': 'New operation',
                    'description': 'a new operation',
                    'job_template': self.job_template_test.id,
                    'type': 'CREATE',
                    'process_timeout_second': 60,
                    "permission": FormUtils.get_default_permission_for_operation(),
                }
            ),
            TestingGetContextView(
                url='service_catalog:operation_details',
                perm_str_list=['service_catalog.view_operation'],
                url_kwargs={'pk': self.create_operation_test.id}
            ),
            TestingGetContextView(
                url='service_catalog:operation_edit',
                perm_str_list=['service_catalog.change_operation'],
                url_kwargs={'pk': self.create_operation_test.id}
            ),
            TestingPostContextView(
                url='service_catalog:operation_edit',
                perm_str_list=['service_catalog.change_operation'],
                url_kwargs={'pk': self.create_operation_test.id},
                data={
                    'service': self.create_operation_test.service.id,
                    'name': 'Operation updated',
                    'description': 'Updated operation description',
                    'job_template': self.job_template_test.id,
                    'type': 'DELETE',
                    'process_timeout_second': 120,
                    "permission": FormUtils.get_default_permission_for_operation()
                }
            ),
            TestingGetContextView(
                url='service_catalog:operation_edit_survey',
                perm_str_list=['service_catalog.change_operation'],
                url_kwargs={'pk': self.update_operation_test.id}
            ),
            TestingPostContextView(
                url='service_catalog:operation_edit_survey',
                perm_str_list=['service_catalog.change_operation'],
                url_kwargs={'pk': self.update_operation_test.id},
                data={
                    'form-0-id': self.update_operation_test.tower_survey_fields.get(variable='text_variable').id,
                    'form-0-default': 'default_var',
                    'form-1-id': self.update_operation_test.tower_survey_fields.get(variable='multiplechoice_variable').id,
                    'form-1-is_customer_field': 'on',
                    'form-1-default': 'default_var',
                    'form-TOTAL_FORMS': 2,
                    'form-INITIAL_FORMS': 2
                }
            ),
            TestingGetContextView(
                url='service_catalog:operation_delete',
                perm_str_list=['service_catalog.delete_operation'],
                url_kwargs={'pk': self.create_operation_test.id}
            ),
            TestingPostContextView(
                url='service_catalog:operation_delete',
                perm_str_list=['service_catalog.delete_operation'],
                url_kwargs={'pk': self.create_operation_test.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)