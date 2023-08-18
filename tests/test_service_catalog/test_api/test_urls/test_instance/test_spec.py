from service_catalog.models import CustomLink, InstanceState
from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestServiceCatalogInstanceCRUDPermissionsEndpoint(BaseTestRequestAPI, TestPermissionEndpoint):
    def test_user_spec_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_instance_user_spec_details',
                perm_str='service_catalog.view_instance',
                url_kwargs={'pk': self.test_instance.id}
            ),
            TestingPutContextView(
                url='api_instance_user_spec_details',
                perm_str='service_catalog.change_instance',
                data={
                    "key1": "value1",
                    "key2": "value2",
                },
                url_kwargs={'pk': self.test_instance.id}
            ),
            TestingPatchContextView(
                url='api_instance_user_spec_details',
                perm_str='service_catalog.change_instance',
                data={
                    'key1': 'value PATCH',
                },
                url_kwargs={'pk': self.test_instance.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_admin_spec_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_instance_spec_details',
                perm_str='service_catalog.view_admin_spec_instance',
                url_kwargs={'pk': self.test_instance.id}
            ),
            TestingPutContextView(
                url='api_instance_spec_details',
                perm_str='service_catalog.change_admin_spec_instance',
                data={
                    "key1": "value1",
                    "key2": "value2",
                },
                url_kwargs={'pk': self.test_instance.id}
            ),
            TestingPatchContextView(
                url='api_instance_spec_details',
                perm_str='service_catalog.change_admin_spec_instance',
                data={
                    'key1': 'value PATCH',
                },
                url_kwargs={'pk': self.test_instance.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
