from service_catalog.models import InstanceState
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogInstancePermissionsStateMachineViews(BaseTestRequest, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.test_instance.state = InstanceState.DELETED
        self.test_instance.save()

    def test_state_machine_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:instance_archive',
                perm_str_list=['service_catalog.archive_instance'],
                url_kwargs={'pk': self.test_instance.id},
                expected_status_code=302

            ),
            TestingPostContextView(
                url='service_catalog:instance_archive',
                perm_str_list=['service_catalog.archive_instance'],
                url_kwargs={'pk': self.test_instance.id},
                expected_not_allowed_status_code=405,
                expected_status_code=405
            ),
            TestingGetContextView(
                url='service_catalog:instance_unarchive',
                perm_str_list=['service_catalog.unarchive_instance'],
                url_kwargs={'pk': self.test_instance.id},
                expected_status_code = 302

            ),
            TestingPostContextView(
                url='service_catalog:instance_archive',
                perm_str_list=['service_catalog.archive_instance'],
                url_kwargs={'pk': self.test_instance.id},
                expected_not_allowed_status_code=405,
                expected_status_code=405
            )
        ]
        self.run_permissions_tests(testing_view_list)