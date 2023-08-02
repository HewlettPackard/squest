import logging

from rest_framework.serializers import Serializer

from service_catalog.forms import FormGenerator

logger = logging.getLogger(__name__)


class DynamicSurveySerializer(Serializer):

    def __init__(self, *args, **kwargs):
        self.operation = kwargs.pop('operation', None)
        self.squest_instance = kwargs.pop('squest_instance', None)
        self.squest_request = kwargs.pop('squest_request', None)
        super(DynamicSurveySerializer, self).__init__(*args, **kwargs)
        form_generator = FormGenerator(operation=self.operation,
                                       is_api_form=True,
                                       squest_instance=self.squest_instance,
                                       squest_request=self.squest_request)
        self.fields.update(form_generator.generate_form())
        if self.operation is not None and not self.operation.job_template.has_a_survey():
            self.required = False
        elif self.squest_request is not None and not self.squest_request.operation.job_template.has_a_survey():
            self.required = False
