from profiles.models import Permission
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogServicePermissionsViews(BaseTestRequest, TestPermissionEndpoint):
    def test_service_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:service_list',
                perm_str='service_catalog.list_service',
            ),
            TestingGetContextView(
                url='service_catalog:service_create',
                perm_str='service_catalog.add_service',
            ),
            TestingPostContextView(
                url='service_catalog:service_create',
                perm_str='service_catalog.add_service',
                data={
                    'name': 'New service',
                    'description': 'A new service',
                }
            ),
            TestingGetContextView(
                url='service_catalog:service_edit',
                perm_str='service_catalog.change_service',
                url_kwargs={'pk': self.service_test.id}
            ),
            TestingPostContextView(
                url='service_catalog:service_edit',
                perm_str='service_catalog.change_service',
                url_kwargs={'pk': self.service_test.id},
                data={
                    'name': 'Service updated',
                    'description': 'Description of service test updated',
                }
            ),
            TestingGetContextView(
                url='service_catalog:service_delete',
                perm_str='service_catalog.delete_service',
                url_kwargs={'pk': self.service_test.id}
            ),
            TestingPostContextView(
                url='service_catalog:service_delete',
                perm_str='service_catalog.delete_service',
                url_kwargs={'pk': self.service_test.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_request_service_views(self):
        self.empty_role.permissions.add(
            Permission.objects.get(content_type__app_label='profiles', codename='consume_quota_scope'))
        self.create_operation_test_2.is_admin_operation = True
        self.create_operation_test_2.save()
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:request_service',
                perm_str='service_catalog.request_on_service',
                url_kwargs={'service_id': self.service_test.id, 'operation_id': self.create_operation_test.id}
            ),
            TestingPostContextView(
                url='service_catalog:request_service',
                perm_str='service_catalog.request_on_service',
                url_kwargs={'service_id': self.service_test.id, 'operation_id': self.create_operation_test.id},
                data={
                    "0-name": "instance_1",
                    "0-quota_scope": self.test_quota_scope.id,
                    "service_request_wizard_view-current_step": "0",
                },
                expected_status_code=200
            ),
            TestingPostContextView(
                url='service_catalog:request_service',
                perm_str='service_catalog.request_on_service',
                url_kwargs={'service_id': self.service_test.id, 'operation_id': self.create_operation_test.id},
                data={
                    "1-text_variable": "text_value_1",
                    "1-multiplechoice_variable": "text_value_2",
                    "service_request_wizard_view-current_step": "1",
                },
            ),
            TestingGetContextView(
                url='service_catalog:request_service',
                perm_str='service_catalog.admin_request_on_service',
                url_kwargs={'service_id': self.service_test_2.id, 'operation_id': self.create_operation_test_2.id}
            ),
            TestingPostContextView(
                url='service_catalog:request_service',
                perm_str='service_catalog.admin_request_on_service',
                url_kwargs={'service_id': self.service_test_2.id, 'operation_id': self.create_operation_test_2.id},
                data={
                    "0-name": "instance_1",
                    "0-quota_scope": self.test_quota_scope.id,
                    "service_request_wizard_view-current_step": "0",
                },
                expected_status_code=200
            ),
            TestingPostContextView(
                url='service_catalog:request_service',
                perm_str='service_catalog.admin_request_on_service',
                url_kwargs={'service_id': self.service_test_2.id, 'operation_id': self.create_operation_test_2.id},
                data={
                    "1-text_variable": "text_value_1",
                    "1-multiplechoice_variable": "text_value_2",
                    "service_request_wizard_view-current_step": "1",
                },
            ),
        ]
        self.run_permissions_tests(testing_view_list)
