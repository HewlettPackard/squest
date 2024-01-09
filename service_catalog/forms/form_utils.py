import logging
from jinja2 import Template
from jinja2.exceptions import UndefinedError
import inspect

from rest_framework.exceptions import ValidationError

from service_catalog.models import Instance

logger = logging.getLogger(__name__)


class FormUtils:
    @classmethod
    def template_field(cls, jinja_template_string, template_data_dict):
        """
        Template a field value with user and or admin spec
        :param jinja_template_string: string that may contain jinja template markers
        :param template_data_dict: dict context
        :return: templated string
        """
        if template_data_dict is None:
            template_data_dict = dict()
        templated_string = ""
        template = Template(jinja_template_string)
        try:
            templated_string = template.render(template_data_dict)
        except UndefinedError as e:
            logger.warning(f"[template_field] templating error: {e.message}")
            pass
        return templated_string




class SurveyValidator:
    def __init__(self, survey, user, operation, instance, form=None):
        self.survey = survey
        self.user = user
        self.operation = operation
        self.instance = instance
        self._form = form

    def validate_survey(self):
        pass

    def _validate(self):
        self.validate_survey()
        logger.info(f"[Form utils] User validator plugin loaded: {inspect.getfile(self.__class__)}")

    def fail(self, message, field="__all__"):
        """ Raise an exception on "field" with message.
        Keyword arguments:
        message -- str -- message you want to display
        field -- str -- field that contains error, default is "__all_""
        """
        logger.info(
            f"Request blocked by validator {inspect.getfile(self.__class__)} (operation:{self.operation}, user:{self.user}), field:{field}, message: {message}"
        )

        if self._form:
            self._form.add_error(field, message)
        else:
            raise ValidationError({field: message})
