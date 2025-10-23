#!/usr/bin/env python
"""
Test script to verify password masking functionality
"""
from service_catalog.models import Request
from service_catalog.api.serializers.request_serializers import AdminRequestSerializer, AWXRequestSerializer

# Get the request
request = Request.objects.get(pk=1)
print('=== Original fill_in_survey ===')
print(request.fill_in_survey)
print()

# Test AdminRequestSerializer (for UI)
admin_serializer = AdminRequestSerializer(request)
print('=== AdminRequestSerializer.data["full_survey"] (per UI) ===')
print(admin_serializer.data['full_survey'])
print()

# Test AWXRequestSerializer (for AWX)
awx_serializer = AWXRequestSerializer(request)
print('=== AWXRequestSerializer.data["fill_in_survey"] (per AWX) ===')
print(awx_serializer.data['fill_in_survey'])
print()

# Test the new masked property directly
print('=== request.masked_fill_in_survey (per template) ===')
print(request.masked_fill_in_survey)
print()

# Test _get_full_survey_for_awx method
print('=== request._get_full_survey_for_awx() (per AWX integration) ===')
print(request._get_full_survey_for_awx())
print()