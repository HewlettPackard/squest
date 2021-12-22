from django.test import TestCase, override_settings
from django.urls import reverse, NoReverseMatch
import base64


@override_settings(ROOT_URLCONF='squest.monitoring.urls')
class TestMonitoring(TestCase):

    def setUp(self) -> None:
        try:
            self.url = reverse('metrics')
        except NoReverseMatch:
            self.url = None

    @override_settings(METRICS_ENABLED=False)
    @override_settings(ROOT_URLCONF='squest.Squest.urls')
    def test_monitoring_page_disabled(self):
        response = self.client.get("/metrics/")
        self.assertEqual(404, response.status_code)

    @override_settings(METRICS_ENABLED=True)
    def test_monitoring_no_login_provided(self):
        response = self.client.get(self.url)
        self.assertEqual(400, response.status_code)

    @override_settings(METRICS_ENABLED=True)
    @override_settings(METRICS_AUTHORIZATION_PASSWORD="password")
    def test_monitoring_correct_login_provided(self):
        credentials = base64.b64encode(b'admin:password')
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Basic ' + credentials.decode("ascii")
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    @override_settings(METRICS_ENABLED=True)
    @override_settings(METRICS_AUTHORIZATION_PASSWORD="password")
    def test_monitoring_incorrect_login_provided(self):
        credentials = base64.b64encode(b'admin:non_valid')
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Basic ' + credentials.decode("ascii")
        response = self.client.get(self.url)
        self.assertEqual(401, response.status_code)

    @override_settings(METRICS_ENABLED=True)
    @override_settings(METRICS_PASSWORD_PROTECTED=False)
    def test_monitoring_password_protected_disabled(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
