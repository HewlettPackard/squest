from service_catalog.api.serializers.dynamic_survey_serializer import DynamicSurveySerializer
from service_catalog.forms import FormUtils


class AcceptRequestSerializer(DynamicSurveySerializer):
    def __init__(self, *args, **kwargs):
        self.target_request = kwargs.pop('target_request')
        self.user = kwargs.pop('user')
        self.read_only_form = kwargs.get('read_only_form', False)
        kwargs['fill_in_survey'] = FormUtils.apply_user_validator_to_survey(
            job_template_survey=self.target_request.operation.job_template.survey,
            operation_survey= self.target_request.operation.tower_survey_fields)
        super(AcceptRequestSerializer, self).__init__(*args, **kwargs)
        if self.read_only_form:
            self._set_initial_and_default(self.target_request.fill_in_survey)
            self._set_initial_and_default(self.target_request.admin_fill_in_survey)

    def save(self, **kwargs):
        if not self.read_only_form:
            user_provided_survey_fields = dict()
            for field_key, value in self.validated_data.items():
                # tower doesnt allow empty value for choices fields
                if value != '':
                    user_provided_survey_fields[field_key] = str(value)
            self.target_request.update_fill_in_surveys_accept_request(user_provided_survey_fields)
            self.target_request.save()
            # reset the instance state if it was failed (in case of resetting the state)
            self.target_request.instance.reset_to_last_stable_state()
            self.target_request.instance.save()
            return self.target_request
