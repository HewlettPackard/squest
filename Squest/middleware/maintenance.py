from django.conf import settings
from django.shortcuts import render
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_503_SERVICE_UNAVAILABLE

from service_catalog.models.squest_settings import SquestSettings


class MaintenanceMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        response = self.get_response(request)
        squest_settings = SquestSettings.load()
        if (settings.MAINTENANCE_MODE_ENABLED or squest_settings.maintenance_mode_enabled) and not request.user.is_superuser:
            if "/api/" in request.path:
                content = {'maintenance_mode_enabled': True}
                api_response = Response(content, status=HTTP_503_SERVICE_UNAVAILABLE)
                api_response.accepted_renderer = JSONRenderer()
                api_response.accepted_media_type = "application/json"
                api_response.renderer_context = {}
                api_response.render()
                return api_response
            else:
                return render(request, 'maintenance.html', status=HTTP_503_SERVICE_UNAVAILABLE)

        return response
