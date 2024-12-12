from profiles.models import Permission
from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestServiceCatalogOperationPermissionsEndpoint(BaseTestRequestAPI, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.empty_role.permissions.add(Permission.objects.get(content_type__app_label='service_catalog', codename='view_instance'))

    def test_operation_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_operation_list_create',
                perm_str_list=['service_catalog.list_operation'],
            ),
            TestingGetContextView(
                url='api_instance_operation_list',
                perm_str_list=['service_catalog.list_operation'],
                url_kwargs={'instance_id': self.test_instance.id}
            ),
            TestingPostContextView(
                url='api_operation_list_create',
                perm_str_list=['service_catalog.add_operation'],
                data={
                    'service': self.service_test.id,
                    'name': 'New operation',
                    'description': 'a new operation',
                    'job_template': self.job_template_test.id,
                    'type': 'CREATE',
                    'process_timeout_second': 60
                }
            ),
            TestingGetContextView(
                url='api_operation_survey_list_update',
                perm_str_list=['service_catalog.change_operation'],
                url_kwargs={'pk': self.create_operation_test.id}
            ),
            TestingPutContextView(
                url='api_operation_survey_list_update',
                perm_str_list=['service_catalog.change_operation'],
                data=[
                    {'variable': 'text_variable', 'is_customer_field': True, 'default': "text_variable_default"},
                    {'variable': 'multiplechoice_variable', 'is_customer_field': False, 'default': "multiplechoice_variable_default"},
                    {'variable': 'multiselect_var', 'is_customer_field': False, 'default': "multiselect_var_default"},
                    {'variable': 'textarea_var', 'is_customer_field': False, 'default': 'textarea_var_default'},
                    {'variable': 'password_var', 'is_customer_field': True, 'default': "password_var_default"},
                    {'variable': 'integer_var', 'is_customer_field': True, 'default': '1'},
                    {'variable': 'float_var', 'is_customer_field': True, 'default': '2'}
                ],
                url_kwargs={'pk': self.create_operation_test.id}
            ),
            TestingPatchContextView(
                url='api_operation_survey_list_update',
                perm_str_list=['service_catalog.change_operation'],
                url_kwargs={'pk': self.create_operation_test.id},
                expected_not_allowed_status_code=405,
                expected_status_code=405
            ),
            TestingGetContextView(
                url='api_operation_details',
                perm_str_list=['service_catalog.view_operation'],
                url_kwargs={'pk': self.create_operation_test.id}
            ),
            TestingPutContextView(
                url='api_operation_details',
                perm_str_list=['service_catalog.change_operation'],
                data={
                    'service': self.service_test.id,
                    'name': 'Operation PUT',
                    'description': 'an operation description',
                    'job_template': self.job_template_test.id,
                    'type': 'CREATE',
                },
                url_kwargs={'pk': self.create_operation_test.id}
            ),
            TestingPatchContextView(
                url='api_operation_details',
                perm_str_list=['service_catalog.change_operation'],
                data={
                    'name': 'Operation PATCH',
                },
                url_kwargs={'pk': self.create_operation_test.id}
            ),
            TestingDeleteContextView(
                url='api_operation_details',
                perm_str_list=['service_catalog.delete_operation'],
                url_kwargs={'pk': self.create_operation_test.id}
            ),
        ]
        self.run_permissions_tests(testing_view_list)