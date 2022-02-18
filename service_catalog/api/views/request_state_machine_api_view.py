from django.http import QueryDict
from django_fsm import can_proceed
from drf_yasg.utils import swagger_auto_schema
from guardian.shortcuts import get_objects_for_user
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from service_catalog.api.serializers import AcceptRequestSerializer, RequestSerializer, MessageSerializer, \
    RequestMessageSerializer, AdminRequestSerializer
from service_catalog.mail_utils import send_mail_request_update, send_email_request_canceled
from service_catalog.models import Request
from service_catalog.views import process_request


class RequestStateMachine(ViewSet):
    def get_permissions(self):
        if self.action == 'cancel':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(request_body=AcceptRequestSerializer, responses={200: AdminRequestSerializer()})
    @action(detail=True)
    def accept(self, request, pk=None):
        """
        Accept the request and validate/complete the survey : change the state of the request to 'ACCEPTED'.
        """
        target_request = get_object_or_404(Request, id=pk)
        if not can_proceed(target_request.accept):
            raise PermissionDenied
        serializer = AcceptRequestSerializer(data=request.data, target_request=target_request, user=request.user,
                                             read_only_form=False)
        if serializer.is_valid():
            target_request = serializer.save()
            send_mail_request_update(target_request, user_applied_state=request.user)
            return Response(AdminRequestSerializer(target_request).data, status=status.HTTP_200_OK)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={200: 'Survey in JSON'})
    @action(detail=True)
    def get_survey(self, request, pk=None):
        """
        Get the survey prefilled by user/admin.
        """
        target_request = get_object_or_404(Request, id=pk)
        serializer = AcceptRequestSerializer(target_request.full_survey, target_request=target_request, user=request.user, read_only_form=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=MessageSerializer, responses={200: AdminRequestSerializer()})
    @action(detail=True)
    def reject(self, request, pk=None):
        """
        Reject the request : change the state of the request to 'REJECTED'.
        """
        target_request = get_object_or_404(Request, id=pk)
        if not can_proceed(target_request.reject):
            raise PermissionDenied
        data = QueryDict.copy(request.data)
        data['sender'] = request.user.id
        data['request'] = target_request.id
        message = RequestMessageSerializer(data=data)
        if message.is_valid():
            message.save()
        target_request.reject()
        target_request.save()
        send_mail_request_update(target_request, user_applied_state=request.user, message=message)
        return Response(AdminRequestSerializer(target_request).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=MessageSerializer, responses={200: AdminRequestSerializer()})
    @action(detail=True)
    def re_submit(self, request, pk=None):
        """
        Re-submit the request : change the state of the request to 'SUBMITTED'.
        """
        target_request = get_object_or_404(Request, id=pk)
        if not can_proceed(target_request.re_submit):
            raise PermissionDenied
        data = QueryDict.copy(request.data)
        data['sender'] = request.user.id
        data['request'] = target_request.id
        message = RequestMessageSerializer(data=data)
        if message.is_valid():
            message.save()
        target_request.re_submit()
        target_request.save()
        send_mail_request_update(target_request, user_applied_state=request.user, message=message)
        return Response(AdminRequestSerializer(target_request).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=MessageSerializer, responses={200: AdminRequestSerializer()})
    @action(detail=True)
    def need_info(self, request, pk=None):
        """
        Ask for more info : change the state of the request to 'NEED_INFO'.
        """
        target_request = get_object_or_404(Request, id=pk)
        if not can_proceed(target_request.need_info):
            raise PermissionDenied
        data = QueryDict.copy(request.data)
        data['sender'] = request.user.id
        data['request'] = target_request.id
        message = RequestMessageSerializer(data=data)
        if message.is_valid():
            message.save()
        target_request.need_info()
        target_request.save()
        send_mail_request_update(target_request, user_applied_state=request.user, message=message)
        return Response(AdminRequestSerializer(target_request).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=MessageSerializer, responses={200: AdminRequestSerializer()})
    @action(detail=True)
    def process(self, request, pk=None):
        """
        Process the Tower/AWX job : change the state of the request to 'PROCESSING' then 'COMPLETE' or 'FAILED' depending on Tower/AWX job status.
        """
        target_request = get_object_or_404(Request, id=pk)
        if not can_proceed(target_request.process):
            raise PermissionDenied
        message = process_request(request.user, target_request)
        if message:
            return Response(message, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(AdminRequestSerializer(target_request).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: RequestSerializer()})
    @action(detail=True)
    def cancel(self, request, pk=None):
        """
        Cancel the request : change the state of the request to 'CANCELED', when instance still in 'PENDING' state it will be deleted.
        """
        user_requests = get_objects_for_user(request.user, 'service_catalog.cancel_request')
        target_request = get_object_or_404(user_requests, id=pk)
        if not can_proceed(target_request.cancel):
            raise PermissionDenied
        if target_request.cancel():
            target_request.save()
        send_email_request_canceled(target_request,
                                    user_applied_state=request.user,
                                    request_owner_user=target_request.user)
        if request.user.is_superuser:
            return Response(AdminRequestSerializer(target_request).data, status=status.HTTP_200_OK)
        return Response(RequestSerializer(target_request).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: AdminRequestSerializer()})
    @action(detail=True)
    def archive(self, request, pk=None):
        """
        Archive the request : change the state of the request to 'ARCHIVED'.
        """
        target_request = get_object_or_404(Request, id=pk)
        if not can_proceed(target_request.archive):
            raise PermissionDenied
        target_request.archive()
        target_request.save()
        return Response(AdminRequestSerializer(target_request).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: AdminRequestSerializer()})
    @action(detail=True)
    def unarchive(self, request, pk=None):
        """
        Unarchive the request : change the state of the request to 'COMPLETE'.
        """
        target_request = get_object_or_404(Request, id=pk)
        if not can_proceed(target_request.unarchive):
            raise PermissionDenied
        target_request.unarchive()
        target_request.save()
        return Response(AdminRequestSerializer(target_request).data, status=status.HTTP_200_OK)
