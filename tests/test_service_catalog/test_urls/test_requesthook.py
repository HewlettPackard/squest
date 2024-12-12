from service_catalog.models import RequestHook, RequestState
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogRequestHookPermissionsViews(BaseTestRequest, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.request_hook = RequestHook.objects.create(
            name="hook1",
            state=RequestState.FAILED,
            job_template=self.job_template_test
        )

    def test_requesthook_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:requesthook_list',
                perm_str_list=['service_catalog.list_requesthook'],
            ),
            TestingGetContextView(
                url='service_catalog:requesthook_create',
                perm_str_list=['service_catalog.add_requesthook'],
            ),
            TestingPostContextView(
                url='service_catalog:requesthook_create',
                perm_str_list=['service_catalog.add_requesthook'],
                data={
                    "name": "New hook",
                    "state": RequestState.SUBMITTED,
                    "job_template": self.job_template_test.id,
                    "extra_vars": "{}"
                }
            ),
            TestingGetContextView(
                url='service_catalog:requesthook_edit',
                perm_str_list=['service_catalog.change_requesthook'],
                url_kwargs={'pk': self.request_hook.id}
            ),
            TestingPostContextView(
                url='service_catalog:requesthook_edit',
                perm_str_list=['service_catalog.change_requesthook'],
                url_kwargs={'pk': self.request_hook.id},
                data={
                    "name": "Hook updated",
                    "state": RequestState.COMPLETE,
                    "job_template": self.job_template_test.id,
                    "extra_vars": {}
                }
            ),
            TestingGetContextView(
                url='service_catalog:requesthook_delete',
                perm_str_list=['service_catalog.delete_requesthook'],
                url_kwargs={'pk': self.request_hook.id}
            ),
            TestingPostContextView(
                url='service_catalog:requesthook_delete',
                perm_str_list=['service_catalog.delete_requesthook'],
                url_kwargs={'pk': self.request_hook.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)