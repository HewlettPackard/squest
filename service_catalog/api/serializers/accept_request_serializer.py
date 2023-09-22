from rest_framework.serializers import Serializer

from service_catalog.forms import FormGenerator


class AcceptRequestSerializer(Serializer):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.squest_request = kwargs.pop('squest_request', None)
        super(AcceptRequestSerializer, self).__init__(*args, **kwargs)
        form_generator = FormGenerator(user=self.user,
                                       is_api_form=True,
                                       squest_request=self.squest_request)
        self.fields.update(form_generator.generate_form())

    def save(self, **kwargs):
        user_provided_survey_fields = dict()
        for field_key, value in self.validated_data.items():
            # tower does not allow empty value for choices fields
            if isinstance(value, set):
                user_provided_survey_fields[field_key] = list(value)
            elif value != '':
                user_provided_survey_fields[field_key] = value
        self.squest_request.update_fill_in_surveys_accept_request(user_provided_survey_fields)
        self.squest_request.save()
        # reset the instance state if it was failed (in case of resetting the state)
        self.squest_request.instance.reset_to_last_stable_state()
        self.squest_request.instance.save()
        return self.squest_request
