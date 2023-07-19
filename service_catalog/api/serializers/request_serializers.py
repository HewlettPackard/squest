from json import dumps, loads
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, CharField, ValidationError

from Squest.utils.squest_encoder import SquestEncoder
from profiles.api.serializers.user_serializers import UserSerializer
from profiles.models import Scope
from service_catalog.forms import FormUtils
from service_catalog.models.request import Request
from service_catalog.models.message import RequestMessage
from service_catalog.models.services import Service
from service_catalog.models.operations import Operation
from service_catalog.models.operation_type import OperationType
from service_catalog.models.instance import Instance
from service_catalog.api.serializers import DynamicSurveySerializer, InstanceReadSerializer


class ServiceRequestSerializer(ModelSerializer):
    class Meta:
        model = Request
        fields = ['squest_instance_name', 'quota_scope', 'request_comment', 'fill_in_survey']

    squest_instance_name = CharField(
        label="Squest instance name",
        help_text="Help to identify the requested service in the 'Instances' view"
    )
    request_comment = CharField(
        label="Comment",
        help_text="Add a comment to your request",
        required=False
    )

    quota_scope = PrimaryKeyRelatedField(label='Quota', allow_null=True, default=None, required=False,
                                           queryset=Scope.objects.all(),
                                           help_text="Quota")

    def __init__(self, *args, **kwargs):
        self.operation = kwargs.pop('operation', None)
        self.user = kwargs.pop('user', None)
        super(ServiceRequestSerializer, self).__init__(*args, **kwargs)
        # get all field that are not disabled by the admin
        purged_survey = FormUtils.get_available_fields(
            job_template_survey=self.operation.job_template.survey,
            operation_survey=self.operation.tower_survey_fields)
        purged_survey_with_validator = FormUtils.apply_user_validator_to_survey(
            job_template_survey=purged_survey,
            operation_survey=self.operation.tower_survey_fields)
        self.fields['fill_in_survey'] = DynamicSurveySerializer(fill_in_survey=purged_survey_with_validator)
        if not purged_survey.get('spec'):
            self.fields['fill_in_survey'].required = False

    def save(self):
        # create the instance
        instance_name = self.validated_data["squest_instance_name"]
        quota_scope = self.validated_data["quota_scope"]

        new_instance = Instance.objects.create(service=self.operation.service, name=instance_name, quota_scope=quota_scope,
                                               requester=self.user)
        fill_in_survey = loads(dumps(self.validated_data.get("fill_in_survey", {}), cls=SquestEncoder))
        new_request = Request.objects.create(instance=new_instance,
                                             operation=self.operation,
                                             fill_in_survey=fill_in_survey,
                                             user=self.user)

        # save the comment
        message = None
        if "request_comment" in self.validated_data and self.validated_data["request_comment"] is not None:
            comment = self.validated_data["request_comment"]
            message = RequestMessage.objects.create(request=new_request, sender=self.user, content=comment)
        from service_catalog.mail_utils import send_mail_request_update
        send_mail_request_update(target_request=new_request, user_applied_state=new_request.user, message=message)
        return new_request


class OperationRequestSerializer(ModelSerializer):
    class Meta:
        model = Request
        fields = ['request_comment', 'fill_in_survey']

    request_comment = CharField(
        label="Comment",
        help_text="Add a comment to your request",
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.operation = kwargs.pop('operation', None)
        self.instance = kwargs.pop('instance', None)
        self.user = kwargs.pop('user', None)
        super(OperationRequestSerializer, self).__init__(*args, **kwargs)
        # get all field that are not disabled by the admin
        purged_survey = FormUtils.get_available_fields(
            job_template_survey=self.operation.job_template.survey,
            operation_survey=self.operation.tower_survey_fields)
        purged_survey_with_validator = FormUtils.apply_user_validator_to_survey(
            job_template_survey=purged_survey,
            operation_survey=self.operation.tower_survey_fields)
        self.fields['fill_in_survey'] = DynamicSurveySerializer(fill_in_survey=purged_survey_with_validator)

    def save(self, **kwargs):
        fill_in_survey = loads(dumps(self.validated_data.get("fill_in_survey", {}), cls=SquestEncoder))
        new_request = Request.objects.create(instance=self.instance,
                                             operation=self.operation,
                                             fill_in_survey=fill_in_survey,
                                             user=self.user)
        # save the comment
        message = None
        if "request_comment" in self.validated_data and self.validated_data["request_comment"] is not None:
            comment = self.validated_data["request_comment"]
            message = RequestMessage.objects.create(request=new_request, sender=self.user, content=comment)
        from service_catalog.mail_utils import send_mail_request_update
        send_mail_request_update(target_request=new_request, user_applied_state=new_request.user, message=message)
        return new_request


class RequestSerializer(ModelSerializer):
    class Meta:
        model = Request
        exclude = ['periodic_task', 'periodic_task_date_expire', 'failure_message', 'admin_fill_in_survey']
        read_only = True

    instance = InstanceReadSerializer(read_only=True)
    user = UserSerializer(read_only=True)


class AdminRequestSerializer(ModelSerializer):
    class Meta:
        model = Request
        exclude = ['periodic_task', 'periodic_task_date_expire', 'failure_message']

    instance = InstanceReadSerializer(read_only=True)
    user = UserSerializer(read_only=True)
