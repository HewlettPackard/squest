from guardian.shortcuts import get_objects_for_user
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from service_catalog.serializers.request_serializer import RequestSerializer


class RequestList(generics.ListAPIView):
    def get_queryset(self):
        return get_objects_for_user(self.request.user, 'service_catalog.view_request')

    permission_classes = [IsAuthenticated]
    serializer_class = RequestSerializer


class RequestDetails(generics.RetrieveUpdateAPIView):
    def get_queryset(self):
        return get_objects_for_user(self.request.user, 'service_catalog.view_request')

    permission_classes = [IsAuthenticated]
    serializer_class = RequestSerializer
