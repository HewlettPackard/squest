from django.contrib.contenttypes.models import ContentType

from profiles.models import Permission
from service_catalog.models import Operation
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint
from service_catalog.forms.form_utils import FormUtils

class TestServiceCatalogServicePermissionsViews(BaseTestRequest, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        operation_content_type = ContentType.objects.get_for_model(Operation)
        self.update_operation_test_2.permission, _ = Permission.objects.get_or_create(content_type=operation_content_type,
                                                                                   codename="is_admin_operation")
        self.update_operation_test_2.save()
    def test_service_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:service_list',
                perm_str_list=['service_catalog.list_service'],
            ),
            TestingGetContextView(
                url='service_catalog:service_create',
                perm_str_list=['service_catalog.add_service'],
            ),
            TestingPostContextView(
                url='service_catalog:service_create',
                perm_str_list=['service_catalog.add_service'],
                data={
                    'name': 'New service',
                    'description': 'A new service',
                    "permission": FormUtils.get_default_permission_for_operation(),
                }
            ),
            TestingGetContextView(
                url='service_catalog:service_details',
                perm_str_list=['service_catalog.view_service'],
                url_kwargs={'pk': self.service_test.id}
            ),
            TestingGetContextView(
                url='service_catalog:service_edit',
                perm_str_list=['service_catalog.change_service'],
                url_kwargs={'pk': self.service_test.id}
            ),
            TestingPostContextView(
                url='service_catalog:service_edit',
                perm_str_list=['service_catalog.change_service'],
                url_kwargs={'pk': self.service_test.id},
                data={
                    'name': 'Service updated',
                    'description': 'Description of service test updated',
                    "permission": FormUtils.get_default_permission_for_operation(),
                }
            ),
            TestingGetContextView(
                url='service_catalog:service_delete',
                perm_str_list=['service_catalog.delete_service'],
                url_kwargs={'pk': self.service_test.id}
            ),
            TestingPostContextView(
                url='service_catalog:service_delete',
                perm_str_list=['service_catalog.delete_service'],
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
                perm_str_list=['service_catalog.request_on_service', self.create_operation_test.permission.permission_str],
                url_kwargs={'service_id': self.service_test.id, 'operation_id': self.create_operation_test.id}
            ),
            TestingPostContextView(
                url='service_catalog:request_service',
                perm_str_list=['service_catalog.request_on_service', self.create_operation_test.permission.permission_str],
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
                perm_str_list=['service_catalog.request_on_service', self.create_operation_test.permission.permission_str],
                url_kwargs={'service_id': self.service_test.id, 'operation_id': self.create_operation_test.id},
                data={
                    "1-text_variable": "text_value_1",
                    "1-multiplechoice_variable": "text_value_2",
                    "service_request_wizard_view-current_step": "1",
                },
            ),
            TestingGetContextView(
                url='service_catalog:request_service',
                perm_str_list=['service_catalog.request_on_service', self.create_operation_test_2.permission.permission_str],
                url_kwargs={'service_id': self.service_test_2.id, 'operation_id': self.create_operation_test_2.id}
            ),
            TestingPostContextView(
                url='service_catalog:request_service',
                perm_str_list=['service_catalog.request_on_service', self.create_operation_test_2.permission.permission_str],
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
                perm_str_list=['service_catalog.request_on_service', self.create_operation_test_2.permission.permission_str],
                url_kwargs={'service_id': self.service_test_2.id, 'operation_id': self.create_operation_test_2.id},
                data={
                    "1-text_variable": "text_value_1",
                    "1-multiplechoice_variable": "text_value_2",
                    "service_request_wizard_view-current_step": "1",
                },
            ),
        ]
        self.run_permissions_tests(testing_view_list)