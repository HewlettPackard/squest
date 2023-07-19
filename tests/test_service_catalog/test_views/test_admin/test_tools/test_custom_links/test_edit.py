from django.urls import reverse

from service_catalog.models.custom_link import LinkButtonClassChoices
from tests.test_service_catalog.test_views.test_admin.test_tools.test_custom_links.base_test_custom_link import \
    BaseTestCustomLink


class CustomLinksEditViewsTest(BaseTestCustomLink):

    def setUp(self):
        super(CustomLinksEditViewsTest, self).setUp()

        args = {
            "pk": self.test_custom_link.id
        }
        self.url = reverse('service_catalog:customlink_edit', kwargs=args)

    def test_get_page(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_edit_custom_link(self):
        data = {
            "name": "updated_name",
            "text": "updated_text",
            "url": "http://updated.domain",
            "button_class": LinkButtonClassChoices.BLUE

        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(302, response.status_code)
        self.test_custom_link.refresh_from_db()
        self.assertEqual(self.test_custom_link.name, "updated_name")
        self.assertEqual(self.test_custom_link.text, "updated_text")
        self.assertEqual(self.test_custom_link.url, "http://updated.domain")
        self.assertEqual(self.test_custom_link.button_class, LinkButtonClassChoices.BLUE)
