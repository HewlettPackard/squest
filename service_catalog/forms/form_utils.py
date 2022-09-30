import copy
import logging

import urllib3
from jinja2 import Template
from jinja2.exceptions import UndefinedError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class FormUtils:
    @classmethod
    def get_available_fields(cls, job_template_survey, operation_survey):
        """
        Return survey fields from the job template that are active in the operation
        :return: survey dict
        :rtype dict
        """
        # copy the dict
        returned_dict = copy.copy(job_template_survey)
        # cleanup the list
        returned_dict["spec"] = list()
        # loop the original survey
        for survey_filled in job_template_survey.get("spec", []):
            if operation_survey.get(name=survey_filled["variable"]).enabled:
                returned_dict["spec"].append(survey_filled)
        return returned_dict

    @classmethod
    def apply_jinja_template_to_survey(cls, job_template_survey, operation_survey, context=None):
        """
        Apply the "default" field of the operation survey
        :param job_template_survey: json job template config
        :param operation_survey: list of TowerSurveyField
        :param context: dict context to be passed to the template
        :return: Updated survey with templated string from spec
        """
        for survey_filled in job_template_survey.get("spec", []):   # loop all survey config from tower
            target_tower_field = operation_survey.get(name=survey_filled["variable"])
            if target_tower_field.default is not None and target_tower_field.default != "":
                survey_filled["default"] = cls.template_field(target_tower_field.default, context)
        return job_template_survey

    @classmethod
    def apply_user_validator_to_survey(cls, job_template_survey, operation_survey):
        for survey_filled in job_template_survey.get("spec", []):  # loop all survey config from tower
            target_tower_field = operation_survey.get(name=survey_filled["variable"])
            survey_filled["validators"] = list()
            if target_tower_field.validators is not None:
                survey_filled["validators"] = target_tower_field.validators.split(",")
        return job_template_survey

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
