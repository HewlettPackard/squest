"""Squest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from .views import *

#  drf-yasg
from Squest.api.celery_tasks_views import CeleryTaskView
from service_catalog.views import markdown_uploader

schema_view = get_schema_view(
    openapi.Info(
        title="Squest API",
        default_version='v1',
        description="Test description",
        license=openapi.License(name="Apache-2.0 License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('ui/', home, name='home'),
    path('', lambda req: redirect('home')),
    path('admin/', admin.site.urls),
    path('ui/service_catalog/', include('service_catalog.urls')),
    path('ui/resource_tracker/', include('resource_tracker.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/service_catalog/', include('service_catalog.api.urls')),
    path('api/resource_tracker/', include('resource_tracker.api.urls')),
    path('api/profiles/', include('profiles.api.urls')),
    path('api/tasks/<int:task_id>/', CeleryTaskView.as_view(), name='get_task_result'),
    path('ui/profiles/', include('profiles.urls')),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('martor/', include('martor.urls')),
    url(
        r'^api/uploader/$',
        markdown_uploader, name='markdown_uploader_page'
    ),
]

if settings.METRICS_ENABLED:
    urlpatterns += [
        path('metrics/', include('monitoring.urls')),
    ]

# if settings.DEBUG:
#     # static files (images, css, javascript, etc.)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
