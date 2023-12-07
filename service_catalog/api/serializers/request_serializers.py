from json import dumps, loads

from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, CharField

from Squest.utils.squest_encoder import SquestEncoder
from profiles.api.serializers.user_serializers import UserSerializerNested
from profiles.models import Scope
from service_catalog.api.serializers import DynamicSurveySerializer, InstanceReadSerializer
from service_catalog.models.instance import Instance
from service_catalog.models.message import RequestMessage
from service_catalog.models.request import Request


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
        self.fields['fill_in_survey'] = DynamicSurveySerializer(operation=self.operation)

    def validate(self, data):
        super(ServiceRequestSerializer, self).validate(data)
        quota_scope = data.get("quota_scope")
        fill_in_survey = data.get("fill_in_survey")
        # validate the quota if set on one of the fill_in_survey
        if fill_in_survey is not None:
            for field_name, value in fill_in_survey.items():
                # get the tower field
                tower_field = self.operation.tower_survey_fields.get(variable=field_name)
                if tower_field.attribute_definition is not None:
                    # try to find the field in the quota linked to the scope
                    quota_set_on_attribute = quota_scope.quotas.filter(attribute_definition=tower_field.attribute_definition)
                    if quota_set_on_attribute.exists():
                        quota_set_on_attribute = quota_set_on_attribute.first()
                        if value > quota_set_on_attribute.available:
                            raise ValidationError({"fill_in_survey":
                                                       f"Quota limit reached on '{field_name}'. "
                                                       f"Available: {quota_set_on_attribute.available}"})
        return data

    def save(self):
        # create the instance
        instance_name = self.validated_data["squest_instance_name"]
        quota_scope = self.validated_data["quota_scope"]

        new_instance = Instance.objects.create(service=self.operation.service, name=instance_name,
                                               quota_scope=quota_scope,
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
        self.squest_instance = kwargs.pop('instance', None)
        self.user = kwargs.pop('user', None)
        super(OperationRequestSerializer, self).__init__(*args, **kwargs)
        self.fields['fill_in_survey'] = DynamicSurveySerializer(user=self.user,
                                                                operation=self.operation,
                                                                instance=self.squest_instance)

    def save(self, **kwargs):
        fill_in_survey = loads(dumps(self.validated_data.get("fill_in_survey", {}), cls=SquestEncoder))
        new_request = Request.objects.create(instance=self.squest_instance,
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
    user = UserSerializerNested(read_only=True)


class AdminRequestSerializer(ModelSerializer):
    class Meta:
        model = Request
        exclude = ['periodic_task', 'periodic_task_date_expire', 'failure_message']

    instance = InstanceReadSerializer(read_only=True)
    user = UserSerializerNested(read_only=True)
