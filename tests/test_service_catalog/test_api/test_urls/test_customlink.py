from service_catalog.models import CustomLink
from tests.permission_endpoint import TestPermissionEndpoint, TestingGetContextView, TestingPostContextView, \
    TestingPatchContextView, TestingPutContextView, TestingDeleteContextView
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestServiceCatalogCustomLinkPermissionsEndpoint(BaseTestRequestAPI, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.custom_link = CustomLink.objects.create(
            name="test_custom_link",
            text="custom_link",
            url="https://custom-link.domain"
        )

    def test_customlink_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='api_customlink_list_create',
                perm_str='service_catalog.list_customlink',
            ),
            TestingPostContextView(
                url='api_customlink_list_create',
                perm_str='service_catalog.add_customlink',
                data={
                    'name': 'New cusom link',
                    'text': 'new_custom_link',
                    'url': 'https://new-custom-link.domain'
                }
            ),
            TestingGetContextView(
                url='api_customlink_details',
                perm_str='service_catalog.view_customlink',
                url_kwargs={'pk': self.custom_link.id}
            ),
            TestingPutContextView(
                url='api_customlink_details',
                perm_str='service_catalog.change_customlink',
                data={
                    'name': 'Custom link PUT',
                    'text': 'new_custom_link',
                    'url': 'https://new-custom-link.domain'
                },
                url_kwargs={'pk': self.custom_link.id}
            ),
            TestingPatchContextView(
                url='api_customlink_details',
                perm_str='service_catalog.change_customlink',
                data={
                    'name': 'Custom link PATCH',
                },
                url_kwargs={'pk': self.custom_link.id}
            ),
            TestingDeleteContextView(
                url='api_customlink_details',
                perm_str='service_catalog.delete_customlink',
                url_kwargs={'pk': self.custom_link.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
