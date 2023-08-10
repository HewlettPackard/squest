from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogOperationPermissionsViews(BaseTestRequest, TestPermissionEndpoint):
    def test_operation_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:operation_list',
                perm_str='service_catalog.list_operation',
                url_kwargs={'service_id': self.service_test.id}
            ),
            TestingGetContextView(
                url='service_catalog:create_operation_list',
                perm_str='service_catalog.list_operation',
                url_kwargs={'service_id': self.service_test.id}
            ),
            TestingGetContextView(
                url='service_catalog:operation_create',
                perm_str='service_catalog.add_operation',
                url_kwargs={'service_id': self.service_test.id}
            ),
            TestingPostContextView(
                url='service_catalog:operation_create',
                perm_str='service_catalog.add_operation',
                url_kwargs={'service_id': self.service_test.id},
                data={
                    'name': 'New operation',
                    'description': 'a new operation',
                    'job_template': self.job_template_test.id,
                    'type': 'CREATE',
                    'process_timeout_second': 60
                }
            ),
            TestingGetContextView(
                url='service_catalog:operation_details',
                perm_str='service_catalog.view_operation',
                url_kwargs={'service_id': self.service_test.id, 'pk': self.create_operation_test.id}
            ),
            TestingGetContextView(
                url='service_catalog:operation_edit',
                perm_str='service_catalog.change_operation',
                url_kwargs={'service_id': self.service_test.id, 'pk': self.create_operation_test.id}
            ),
            TestingPostContextView(
                url='service_catalog:operation_edit',
                perm_str='service_catalog.change_operation',
                url_kwargs={'service_id': self.service_test.id, 'pk': self.create_operation_test.id},
                data={
                    'name': 'Operation updated',
                    'description': 'Updated operation description',
                    'job_template': self.job_template_test.id,
                    'type': 'DELETE',
                    'process_timeout_second': 120
                }
            ),
            TestingGetContextView(
                url='service_catalog:operation_edit_survey',
                perm_str='service_catalog.change_operation',
                url_kwargs={'service_id': self.service_test.id, 'pk': self.update_operation_test.id}
            ),
            TestingPostContextView(
                url='service_catalog:operation_edit_survey',
                perm_str='service_catalog.change_operation',
                url_kwargs={'service_id': self.service_test.id, 'pk': self.update_operation_test.id},
                data={
                    'form-0-id': self.update_operation_test.tower_survey_fields.get(name='text_variable').id,
                    'form-0-default': 'default_var',
                    'form-1-id': self.update_operation_test.tower_survey_fields.get(name='multiplechoice_variable').id,
                    'form-1-is_customer_field': 'on',
                    'form-1-default': 'default_var',
                    'form-TOTAL_FORMS': 2,
                    'form-INITIAL_FORMS': 2
                }
            ),
            TestingGetContextView(
                url='service_catalog:operation_delete',
                perm_str='service_catalog.delete_operation',
                url_kwargs={'service_id': self.service_test.id, 'pk': self.create_operation_test.id}
            ),
            TestingPostContextView(
                url='service_catalog:operation_delete',
                perm_str='service_catalog.delete_operation',
                url_kwargs={'service_id': self.service_test.id, 'pk': self.create_operation_test.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
