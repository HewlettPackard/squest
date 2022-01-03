import base64
import logging

import prometheus_client
from django.http import HttpResponse
from django.conf import settings

logger = logging.getLogger(__name__)


def metrics(request):
    """
    Exports /metrics as a Django view.
    """
    metrics_password_protected = getattr(
        settings, "METRICS_PASSWORD_PROTECTED", False)

    if metrics_password_protected:
        expected_username = getattr(
            settings, "METRICS_AUTHORIZATION_USERNAME", None)
        expected_password = getattr(
            settings, "METRICS_AUTHORIZATION_PASSWORD", None)
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        token_type, _, credentials = auth_header.partition(" ")
        if credentials == '':
            logger.debug(f"[metrics] credentials not provided")
            response = HttpResponse('Authorization Required', status=401)
            response['WWW-Authenticate'] = 'Basic realm="Login Required"'
            return response

        received_auth_string = base64.b64decode(credentials).decode()
        if ':' not in received_auth_string:
            logger.debug(f"[metrics] Invalid credentials format")
            response = HttpResponse('Authorization Required', status=400)
            response['WWW-Authenticate'] = 'Basic realm="Login Required"'
            return response

        received_username = received_auth_string.split(':')[0]
        received_password = received_auth_string.split(':')[1]

        valid_username = received_username == expected_username
        valid_password = received_password == expected_password

        if token_type != 'Basic' or not valid_username or not valid_password:
            logger.debug(f"[metrics] invalid credentials")
            response = HttpResponse('Invalid credentials', status=401)
            response['WWW-Authenticate'] = 'Basic realm="Login Required"'
            return response

    registry = prometheus_client.REGISTRY
    metrics_page = prometheus_client.generate_latest(registry)
    return HttpResponse(
        metrics_page, content_type=prometheus_client.CONTENT_TYPE_LATEST
    )
