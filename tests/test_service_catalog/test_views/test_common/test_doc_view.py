from django.urls import reverse

from service_catalog.models.documentation import Doc
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestCustomerCatalogViews(BaseTestRequest):

    def setUp(self):
        super(TestCustomerCatalogViews, self).setUp()
        self.client.login(username=self.standard_user, password=self.common_password)

        self.new_doc = Doc.objects.create(title="test_doc", content="# tittle 1")
        self.new_doc.services.add(self.service_test)

    def _test_can_list_doc(self):
        url = reverse('service_catalog:doc_list')
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        self.assertTrue("table" in response.context)
        self.assertEquals(response.context["table"].data.data.count(), 1)

    def test_customer_can_list_doc(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        self._test_can_list_doc()

    def test_admin_can_list_doc(self):
        self._test_can_list_doc()

    def test_cannot_get_doc_list_when_logout(self):
        self.client.logout()
        url = reverse('service_catalog:doc_list')
        response = self.client.get(url)
        self.assertEquals(302, response.status_code)

    def test_admin_can_list_admin_doc_list(self):
        self.client.login(username=self.superuser, password=self.common_password)
        url = reverse('admin:service_catalog_doc_changelist')
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)

    def test_admin_can_edit_admin_doc(self):
        self.client.login(username=self.superuser, password=self.common_password)
        url = reverse('admin:service_catalog_doc_change', args=[self.new_doc.id])
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)

    def test_customer_cannot_edit_admin_doc(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        url = reverse('admin:service_catalog_doc_change', args=[self.new_doc.id])
        response = self.client.get(url)
        self.assertEquals(302, response.status_code)
        self.assertTrue("next=/admin", response.url)

    def test_cannot_edit_admin_doc_when_logout(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        url = reverse('admin:service_catalog_doc_change', args=[self.new_doc.id])
        response = self.client.get(url)
        self.assertEquals(302, response.status_code)

    def test_customer_cannot_list_admin_doc(self):
        self.client.login(username=self.standard_user, password=self.common_password)
        url = reverse('admin:service_catalog_doc_changelist')
        response = self.client.get(url)
        self.assertEquals(302, response.status_code)
        self.assertTrue("next=/admin", response.url)
