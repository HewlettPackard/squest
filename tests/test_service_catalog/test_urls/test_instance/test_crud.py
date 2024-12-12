import json

from service_catalog.models import InstanceState
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogInstancePermissionsCRUDViews(BaseTestRequest, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.test_instance.state = InstanceState.AVAILABLE
        self.test_instance_2.state = InstanceState.AVAILABLE
        self.test_instance_2.service = self.update_operation_test_2.service
        self.test_instance.save()
        self.test_instance_2.save()

        self.update_operation_test_2.is_admin_operation = True
        self.update_operation_test_2.save()

    def test_crud_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:instance_list',
                perm_str_list=['service_catalog.list_instance'],
            ),
            TestingGetContextView(
                url='service_catalog:instance_details',
                perm_str_list=['service_catalog.view_instance'],
                url_kwargs={'pk': self.test_instance.id}
            ),
            TestingGetContextView(
                url='service_catalog:instance_request_new_operation',
                perm_str_list=['service_catalog.request_on_instance'],
                url_kwargs={'instance_id': self.test_instance.id, 'operation_id': self.update_operation_test.id}
            ),
            TestingPostContextView(
                url='service_catalog:instance_request_new_operation',
                perm_str_list=['service_catalog.request_on_instance'],
                url_kwargs={'instance_id': self.test_instance.id, 'operation_id': self.update_operation_test.id},
                data={
                    'text_variable': 'test'
                }
            ),
            TestingGetContextView(
                url='service_catalog:instance_request_new_operation',
                perm_str_list=['service_catalog.admin_request_on_instance'],
                url_kwargs={'instance_id': self.test_instance_2.id, 'operation_id': self.update_operation_test_2.id}
            ),
            TestingPostContextView(
                url='service_catalog:instance_request_new_operation',
                perm_str_list=['service_catalog.admin_request_on_instance'],
                url_kwargs={'instance_id': self.test_instance_2.id, 'operation_id': self.update_operation_test_2.id},
                data={
                    'text_variable': 'test'
                }
            ),
            TestingGetContextView(
                url='service_catalog:instance_edit',
                perm_str_list=['service_catalog.change_instance'],
                url_kwargs={'pk': self.test_instance.id}
            ),
            TestingPostContextView(
                url='service_catalog:instance_edit',
                perm_str_list=['service_catalog.change_instance'],
                url_kwargs={'pk': self.test_instance.id},
                data={
                    'name': 'new_instance_name',
                    'service': self.service_test_2.id,
                    'requester': self.standard_user_2.id,
                    'state': InstanceState.PROVISIONING,
                    'quota_scope': self.test_quota_scope.id,
                    'spec': json.dumps({"key1": "val1", "key2": "val2"}),
                    'user_spec': json.dumps({"key1": "val1", "key2": "val2"}),
                }
            ),
            TestingGetContextView(
                url='service_catalog:instance_delete',
                perm_str_list=['service_catalog.delete_instance'],
                url_kwargs={'pk': self.test_instance.id}
            ),
            TestingPostContextView(
                url='service_catalog:instance_delete',
                perm_str_list=['service_catalog.delete_instance'],
                url_kwargs={'pk': self.test_instance.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)