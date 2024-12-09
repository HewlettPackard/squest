from service_catalog.models import CustomLink, InstanceState
from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestServiceCatalogInstanceCRUDPermissionsEndpoint(BaseTestRequestAPI, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.test_instance.state = InstanceState.AVAILABLE
        self.test_instance_2.state = InstanceState.AVAILABLE
        self.test_instance_2.service = self.update_operation_test_2.service
        self.test_instance.save()
        self.test_instance_2.save()

        self.update_operation_test_2.is_admin_operation = True
        self.update_operation_test_2.save()

    def test_instance_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_instance_list_create',
                perm_str='service_catalog.list_instance',
            ),
            TestingPostContextView(
                url='api_instance_list_create',
                perm_str='service_catalog.add_instance',
                data={
                    "name": "New instance",
                    "service": self.service_test_2.id,
                    "requester": self.standard_user_2.id,
                    "state": InstanceState.AVAILABLE,
                    "quota_scope": self.test_quota_scope_org.id,
                    "spec": {
                        "key1": "val1",
                        "key2": "val2"
                    }
                }
            ),
            TestingGetContextView(
                url='api_operation_request_create',
                perm_str='service_catalog.view_request',
                url_kwargs={'instance_id': self.test_instance.id, 'operation_id': self.update_operation_test.id},
                expected_status_code=405,
                expected_not_allowed_status_code=405
            ),
            TestingPostContextView(
                url='api_operation_request_create',
                perm_str='service_catalog.request_on_instance',
                url_kwargs={'instance_id': self.test_instance.id, 'operation_id': self.update_operation_test.id},
                data={
                    'fill_in_survey': {
                        'text_variable': 'test'
                    }}
            ),
            TestingGetContextView(
                url='api_operation_request_create',
                perm_str='service_catalog.view_request',
                url_kwargs={'instance_id': self.test_instance_2.id, 'operation_id': self.update_operation_test_2.id},
                expected_status_code=405,
                expected_not_allowed_status_code=405
            ),
            TestingPostContextView(
                url='api_operation_request_create',
                perm_str=self.update_operation_test_2.permission.permission_str,
                url_kwargs={'instance_id': self.test_instance_2.id, 'operation_id': self.update_operation_test_2.id},
                data={
                    'fill_in_survey': {
                        'text_variable': 'test'
                    }
                }
            ),
            TestingGetContextView(
                url='api_instance_details',
                perm_str='service_catalog.view_instance',
                url_kwargs={'pk': self.test_instance.id}
            ),
            TestingPutContextView(
                url='api_instance_details',
                perm_str='service_catalog.change_instance',
                data={
                    'name': 'Instance PUT',
                    "service": self.service_test_2.id,
                    "requester": self.standard_user_2.id,
                    "state": InstanceState.AVAILABLE,
                    "quota_scope": self.test_quota_scope_org.id,
                    "spec": {
                        "key1": "val1",
                        "key2": "val2"
                    }
                },
                url_kwargs={'pk': self.test_instance.id}
            ),
            TestingPatchContextView(
                url='api_instance_details',
                perm_str='service_catalog.change_instance',
                data={
                    'name': 'Instance PATCH',
                },
                url_kwargs={'pk': self.test_instance.id}
            ),
            TestingDeleteContextView(
                url='api_instance_details',
                perm_str='service_catalog.delete_instance',
                url_kwargs={'pk': self.test_instance.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)