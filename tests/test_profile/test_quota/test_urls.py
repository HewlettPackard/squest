from django.urls import reverse

from profiles.models import QuotaBinding, QuotaAttributeDefinition
from tests.test_profile.test_quota.base_test_quota import BaseTestQuota


class TestQuotaUrls(BaseTestQuota):

    def setUp(self):
        super(TestQuotaUrls, self).setUp()
        self.args_billing = {
            'billing_group_id': self.test_billing_group.id
        }
        self.test_quota_binding = self.test_billing_group.quota_bindings.first()
        self.args_quota_binding = {
            'quota_binding_id': self.test_quota_binding.id
        }
        self.test_quota_attribute = self.test_billing_group.quota_bindings.first().quota_attribute_definition
        self.args_quota_attribute = {
            'quota_attribute_definition_id': self.test_quota_attribute.id
        }

    def test_quota_binding_edit(self):
        url = reverse('profiles:quota_binding_edit', kwargs={**self.args_billing, **self.args_quota_binding})
        self._check_get_page(url)
        self.assertEqual(self.test_quota_binding.limit, 0)
        self._check_post_page(url, data={'limit': 100})
        self.test_quota_binding.refresh_from_db()
        self.assertEqual(self.test_quota_binding.limit, 100)
        self.client.logout()
        self._check_get_page(url, 302)

    def test_quota_binding_delete(self):
        url = reverse('profiles:quota_binding_delete', kwargs={**self.args_billing, **self.args_quota_binding})
        binding_id = self.test_quota_binding.id
        self._check_get_page(url)
        self.assertNotEqual(0, QuotaBinding.objects.filter(id=binding_id).count())
        count = QuotaBinding.objects.count()
        self._check_post_page(url)
        self.assertEqual(0, QuotaBinding.objects.filter(id=binding_id).count())
        self.assertEqual(count - 1, QuotaBinding.objects.count())
        self.client.logout()
        self._check_get_page(url, 302)

    def test_quota_binding_edit_all(self):
        url = reverse('profiles:quota_binding_edit_all', kwargs=self.args_billing)
        self._check_get_page(url)
        self.assertEqual(2, self.test_billing_group.quota_bindings.count())
        self._check_post_page(url, data={'quota_attribute_definition': [self.test_quota_attribute_cpu.id]})
        self.assertEqual(1, self.test_billing_group.quota_bindings.count())
        self.client.logout()
        self._check_get_page(url, 302)

    def test_quota_binding_set_limits(self):
        url = reverse('profiles:quota_binding_set_limits', kwargs=self.args_billing)
        self._check_get_page(url)
        self._check_post_page(url, data={self.test_quota_attribute_cpu.name: 50}, status=200)
        self._check_post_page(reverse('profiles:quota_binding_edit_all', kwargs=self.args_billing),
                              data={'quota_attribute_definition': [self.test_quota_attribute_cpu.id]})
        self._check_post_page(url, data={self.test_quota_attribute_cpu.name: 50})
        binding = self.test_billing_group.quota_bindings.get(quota_attribute_definition=self.test_quota_attribute_cpu)
        self.assertEqual(binding.limit, 50)
        self.client.logout()
        self._check_get_page(url, 302)

    def test_quota_attribute_definition_list(self):
        url = reverse('profiles:quota_attribute_definition_list')
        response = self._check_get_page(url)
        self.assertNotEqual(QuotaAttributeDefinition.objects.count(), 0)
        self.assertEqual(QuotaAttributeDefinition.objects.count(), len(response.context["table"].data.data))
        self.client.logout()
        self._check_get_page(url, 302)

    def test_quota_attribute_definition_create(self):
        url = reverse('profiles:quota_attribute_definition_create')
        self._check_get_page(url)
        self.assertEqual(0, QuotaAttributeDefinition.objects.filter(name='new name').count())
        count = QuotaAttributeDefinition.objects.count()
        self._check_post_page(
            url,
            data={'name': 'new name', 'quota_attribute_definition': [self.test_quota_attribute_cpu.id]}
        )
        self.assertEqual(count + 1, QuotaAttributeDefinition.objects.count())
        self.assertNotEqual(0, QuotaAttributeDefinition.objects.filter(name='new name').count())
        self.client.logout()
        self._check_get_page(url, 302)

    def test_quota_attribute_definition_edit(self):
        url = reverse('profiles:quota_attribute_definition_edit', kwargs=self.args_quota_attribute)
        self._check_get_page(url)
        self.assertEqual(0, QuotaAttributeDefinition.objects.filter(name='new name').count())
        self._check_post_page(
            url,
            data={'name': 'new name', 'quota_attribute_definition': [self.test_quota_attribute_cpu.id]}
        )
        self.assertEqual(1, QuotaAttributeDefinition.objects.filter(name='new name').count())
        self.client.logout()
        self._check_get_page(url, 302)

    def test_quota_attribute_definition_delete(self):
        url = reverse('profiles:quota_attribute_definition_delete', kwargs=self.args_quota_attribute)
        self._check_get_page(url)
        quota_attribute_id = self.test_quota_binding.id
        self.assertNotEqual(0, QuotaAttributeDefinition.objects.filter(id=quota_attribute_id).count())
        count = QuotaAttributeDefinition.objects.count()
        self._check_post_page(url)
        self.assertEqual(0, QuotaAttributeDefinition.objects.filter(id=quota_attribute_id).count())
        self.assertEqual(count - 1, QuotaAttributeDefinition.objects.count())
        self.client.logout()
        self._check_get_page(url, 302)

    def _check_get_page(self, url, status=200):
        response = self.client.get(url)
        self.assertEqual(status, response.status_code)
        return response

    def _check_post_page(self, url, data=None, status=302):
        response = self.client.post(url, data=data)
        self.assertEqual(status, response.status_code)
        return response
