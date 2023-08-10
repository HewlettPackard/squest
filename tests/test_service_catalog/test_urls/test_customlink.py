from service_catalog.models import CustomLink
from service_catalog.models.custom_link import LinkButtonClassChoices
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogCustomLinkPermissionsViews(BaseTestRequest, TestPermissionEndpoint):
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
                url='service_catalog:customlink_list',
                perm_str='service_catalog.list_customlink',
            ),
            TestingGetContextView(
                url='service_catalog:customlink_create',
                perm_str='service_catalog.add_customlink',
            ),
            TestingPostContextView(
                url='service_catalog:customlink_create',
                perm_str='service_catalog.add_customlink',
                data={
                    "name": "custom_link_1",
                    "text": "custom_link__text_1",
                    "url": "http://example.domain",
                    "button_class": LinkButtonClassChoices.DEFAULT
                }
            ),
            TestingGetContextView(
                url='service_catalog:customlink_edit',
                perm_str='service_catalog.change_customlink',
                url_kwargs={'pk': self.custom_link.id}
            ),
            TestingPostContextView(
                url='service_catalog:customlink_edit',
                perm_str='service_catalog.change_customlink',
                url_kwargs={'pk': self.custom_link.id},
                data={
                    "name": "updated_name",
                    "text": "updated_text",
                    "url": "http://updated.domain",
                    "button_class": LinkButtonClassChoices.BLUE
                }
            ),
            TestingGetContextView(
                url='service_catalog:customlink_delete',
                perm_str='service_catalog.delete_customlink',
                url_kwargs={'pk': self.custom_link.id}
            ),
            TestingPostContextView(
                url='service_catalog:customlink_delete',
                perm_str='service_catalog.delete_customlink',
                url_kwargs={'pk': self.custom_link.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
