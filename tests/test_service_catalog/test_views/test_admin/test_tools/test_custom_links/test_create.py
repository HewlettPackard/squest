from django.urls import reverse

from service_catalog.models import GlobalHook, CustomLink
from service_catalog.models.custom_link import LinkButtonClassChoices
from tests.test_service_catalog.base import BaseTest
from tests.test_service_catalog.test_views.test_admin.test_tools.test_custom_links.base_test_custom_link import \
    BaseTestCustomLink


class CustomLinksCreateViewsTest(BaseTestCustomLink):

    def setUp(self):
        super(CustomLinksCreateViewsTest, self).setUp()
        self.url = reverse('service_catalog:customlink_create')
        self.number_custom_link_before = CustomLink.objects.all().count()

    def test_get_page(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_create_custom_link(self):
        data = {
            "name": "custom_link_1",
            "text": "custom_link__text_1",
            "url": "http://example.domain",
            "button_class": LinkButtonClassChoices.DEFAULT
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(self.number_custom_link_before + 1, CustomLink.objects.all().count())
