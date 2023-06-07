from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from service_catalog.models.squest_settings import SquestSettings
from tests.test_service_catalog.base import BaseTest
from rest_framework.test import APIClient

CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }


@override_settings(CACHES=CACHES)
class TestSquestSettings(BaseTest):

    def _check_squest_access(self):
        # as an admin I can still access
        url = reverse('service_catalog:instance_list')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # from the api
        self.url = reverse('api_instance_list')
        api_client = APIClient()
        api_client.force_authenticate(user=self.superuser)
        response = api_client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # as end user I have no longer access to Squest
        self.client.force_login(user=self.standard_user)
        response = self.client.get(url)
        self.assertEqual(503, response.status_code)

        # from the api
        api_client.force_authenticate(user=self.standard_user)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_access_squest_when_maintenance_enabled_from_model_settings(self):
        squest_settings = SquestSettings.load()
        squest_settings.maintenance_mode_enabled = True
        squest_settings.save()
        self._check_squest_access()

    @override_settings(MAINTENANCE_MODE_ENABLED=True)
    def test_access_squest_when_maintenance_enabled_from_squest_settings(self):
        self._check_squest_access()
