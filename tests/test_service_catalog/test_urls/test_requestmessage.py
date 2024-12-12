from service_catalog.models import RequestMessage
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogRequestMessagePermissionsViews(BaseTestRequest, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.request_message = RequestMessage.objects.create(
            sender=self.testing_user,
            request=self.test_request,
            content="Existing message"
        )

    def test_requestmessage_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:requestmessage_create',
                perm_str_list=['service_catalog.add_requestmessage'],
                url_kwargs={'request_id': self.test_request.id}
            ),
            TestingPostContextView(
                url='service_catalog:requestmessage_create',
                perm_str_list=['service_catalog.add_requestmessage'],
                url_kwargs={'request_id': self.test_request.id},
                data={
                    'content': 'new message'
                }
            ),
            TestingGetContextView(
                url='service_catalog:requestmessage_edit',
                perm_str_list=['service_catalog.change_requestmessage'],
                url_kwargs={'request_id': self.test_request.id, 'pk': self.request_message.id}
            ),
            TestingPostContextView(
                url='service_catalog:requestmessage_edit',
                perm_str_list=['service_catalog.change_requestmessage'],
                url_kwargs={'request_id': self.test_request.id, 'pk': self.request_message.id},
                data={
                    'content': 'message updated'
                }
            )
        ]
        self.run_permissions_tests(testing_view_list)