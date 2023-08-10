from service_catalog.models import GlobalHook
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogGlobalHookPermissionsViews(BaseTestRequest, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.global_hook = GlobalHook.objects.create(
            name="hook1",
            model="Instance",
            state="PROVISIONING",
            job_template=self.job_template_test
        )
        
    def test_globalhook_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:globalhook_list',
                perm_str='service_catalog.list_globalhook',
            ),
            TestingGetContextView(
                url='service_catalog:globalhook_create',
                perm_str='service_catalog.add_globalhook',
            ),
            TestingPostContextView(
                url='service_catalog:globalhook_create',
                perm_str='service_catalog.add_globalhook',
                data={
                    "name": "New hook",
                    "model": "Instance",
                    "state": "PROVISIONING",
                    "job_template": self.job_template_test.id,
                    "extra_vars": "{}"
                }
            ),
            TestingGetContextView(
                url='service_catalog:globalhook_edit',
                perm_str='service_catalog.change_globalhook',
                url_kwargs={'pk': self.global_hook.id}
            ),
            TestingPostContextView(
                url='service_catalog:globalhook_edit',
                perm_str='service_catalog.change_globalhook',
                url_kwargs={'pk': self.global_hook.id},
                data={
                    "name": "Hook updated",
                    "model": "Instance",
                    "state": "PENDING",
                    "job_template": self.job_template_test.id,
                    "extra_vars": {}
                }
            ),
            TestingPostContextView(
                url='service_catalog:ajax_load_model_state',
                perm_str='service_catalog.add_globalhook',
                expected_status_code=405,
                expected_not_allowed_status_code=405
            ),
            TestingGetContextView(
                url='service_catalog:ajax_load_model_state',
                perm_str='service_catalog.add_globalhook',
                data={
                    "model": 'Instance'
                }
            ),
            TestingGetContextView(
                url='service_catalog:ajax_load_model_state',
                perm_str='service_catalog.change_globalhook',
                data={
                    "model": 'Instance'
                }
            ),
            TestingPostContextView(
                url='service_catalog:ajax_load_service_operations',
                perm_str='service_catalog.change_globalhook',
                expected_status_code=405,
                expected_not_allowed_status_code=405
            ),
            TestingGetContextView(
                url='service_catalog:ajax_load_service_operations',
                perm_str='service_catalog.add_globalhook',
                data={
                    'service': self.service_test.id
                }
            ),
            TestingGetContextView(
                url='service_catalog:ajax_load_service_operations',
                perm_str='service_catalog.change_globalhook',
                data={
                    'service': self.service_test.id
                }
            ),
            TestingGetContextView(
                url='service_catalog:globalhook_delete',
                perm_str='service_catalog.delete_globalhook',
                url_kwargs={'pk': self.global_hook.id}
            ),
            TestingPostContextView(
                url='service_catalog:globalhook_delete',
                perm_str='service_catalog.delete_globalhook',
                url_kwargs={'pk': self.global_hook.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
