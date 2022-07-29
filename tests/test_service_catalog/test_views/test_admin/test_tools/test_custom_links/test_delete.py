from django.urls import reverse

from service_catalog.models import CustomLink
from tests.test_service_catalog.test_views.test_admin.test_tools.test_custom_links.base_test_custom_link import \
    BaseTestCustomLink


class CustomLinksDeleteViewsTest(BaseTestCustomLink):

    def setUp(self):
        super(CustomLinksDeleteViewsTest, self).setUp()
        args = {
            "custom_link_id": self.test_custom_link.id
        }
        self.url = reverse('service_catalog:custom_link_delete', kwargs=args)

    def test_can_delete_custom_link(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

        id_to_delete = self.test_custom_link.id
        response = self.client.post(self.url)
        self.assertEqual(302, response.status_code)
        self.assertFalse(CustomLink.objects.filter(id=id_to_delete).exists())

    def test_cannot_delete_custom_link_when_logout(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(302, response.status_code)
