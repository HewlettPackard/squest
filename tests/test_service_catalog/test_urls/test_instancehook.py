from service_catalog.models import InstanceHook, InstanceState
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogInstanceHookPermissionsViews(BaseTestRequest, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.instance_hook = InstanceHook.objects.create(
            name="hook1",
            state=InstanceState.PROVISIONING,
            job_template=self.job_template_test
        )

    def test_instancehook_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:instancehook_list',
                perm_str_list=['service_catalog.list_instancehook'],
            ),
            TestingGetContextView(
                url='service_catalog:instancehook_create',
                perm_str_list=['service_catalog.add_instancehook'],
            ),
            TestingPostContextView(
                url='service_catalog:instancehook_create',
                perm_str_list=['service_catalog.add_instancehook'],
                data={
                    "name": "New hook",
                    "state": InstanceState.PROVISIONING,
                    "job_template": self.job_template_test.id,
                    "extra_vars": "{}"
                }
            ),
            TestingGetContextView(
                url='service_catalog:instancehook_edit',
                perm_str_list=['service_catalog.change_instancehook'],
                url_kwargs={'pk': self.instance_hook.id}
            ),
            TestingPostContextView(
                url='service_catalog:instancehook_edit',
                perm_str_list=['service_catalog.change_instancehook'],
                url_kwargs={'pk': self.instance_hook.id},
                data={
                    "name": "Hook updated",
                    "state": InstanceState.PENDING,
                    "job_template": self.job_template_test.id,
                    "extra_vars": {}
                }
            ),
            TestingGetContextView(
                url='service_catalog:instancehook_delete',
                perm_str_list=['service_catalog.delete_instancehook'],
                url_kwargs={'pk': self.instance_hook.id}
            ),
            TestingPostContextView(
                url='service_catalog:instancehook_delete',
                perm_str_list=['service_catalog.delete_instancehook'],
                url_kwargs={'pk': self.instance_hook.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)