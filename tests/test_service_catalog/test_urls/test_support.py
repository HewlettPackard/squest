
from service_catalog.models import SupportMessage
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogSupportPermissionsViews(BaseTestRequest, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.test_message = SupportMessage.objects.create(
            support=self.support_test,
            content='test',
            sender=self.testing_user
        )

    def test_support_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:support_list',
                perm_str='service_catalog.list_support',
            ),
            TestingGetContextView(
                url='service_catalog:support_create',
                perm_str='service_catalog.add_support',
                url_kwargs={'instance_id': self.support_test.instance.id}
            ),
            TestingPostContextView(
                url='service_catalog:support_create',
                perm_str='service_catalog.add_support',
                data={
                    'title': 'New support',
                    'content': 'message'
                },
                url_kwargs={'instance_id': self.support_test.instance.id}
            ),
            TestingGetContextView(
                url='service_catalog:support_details',
                perm_str='service_catalog.view_support',
                url_kwargs={'instance_id': self.support_test.instance.id, 'pk': self.support_test.id},
            ),
            TestingPostContextView(
                url='service_catalog:support_details',
                perm_str='service_catalog.add_supportmessage',
                url_kwargs={'instance_id': self.support_test.instance.id, 'pk': self.support_test.id},
                data={
                    'content': 'message'
                }
            ),
            TestingGetContextView(
                url='service_catalog:supportmessage_edit',
                perm_str='service_catalog.change_supportmessage',
                url_kwargs={'instance_id': self.support_test.instance.id, 'support_id': self.support_test.id,
                            'pk': self.test_message.id},
            ),
            TestingPostContextView(
                url='service_catalog:supportmessage_edit',
                perm_str='service_catalog.change_supportmessage',
                url_kwargs={'instance_id': self.support_test.instance.id, 'support_id': self.support_test.id,
                            'pk': self.test_message.id},
                data={
                    'content': 'message'
                }
            ),
            TestingGetContextView(
                url='service_catalog:support_close',
                perm_str='service_catalog.close_support',
                url_kwargs={'instance_id': self.support_test.instance.id, 'pk': self.support_test.id},
                expected_status_code=302
            ),
            TestingPostContextView(
                url='service_catalog:support_close',
                perm_str='service_catalog.close_support',
                url_kwargs={'instance_id': self.support_test.instance.id, 'pk': self.support_test.id},
                expected_status_code=405,
                expected_not_allowed_status_code=405
            ),
            TestingGetContextView(
                url='service_catalog:support_reopen',
                perm_str='service_catalog.reopen_support',
                url_kwargs={'instance_id': self.support_test.instance.id, 'pk': self.support_test.id},
                expected_status_code=302
            ),
            TestingPostContextView(
                url='service_catalog:support_reopen',
                perm_str='service_catalog.reopen_support',
                url_kwargs={'instance_id': self.support_test.instance.id, 'pk': self.support_test.id},
                expected_status_code=405,
                expected_not_allowed_status_code=405
            ),
            TestingGetContextView(
                url='service_catalog:support_delete',
                perm_str='service_catalog.delete_support',
                url_kwargs={'instance_id': self.support_test.instance.id, 'pk': self.support_test.id},
            ),
            TestingPostContextView(
                url='service_catalog:support_delete',
                perm_str='service_catalog.delete_support',
                url_kwargs={'instance_id': self.support_test.instance.id, 'pk': self.support_test.id}
            ),
        ]
        self.run_permissions_tests(testing_view_list)
