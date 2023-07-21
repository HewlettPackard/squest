import copy
import logging

from jinja2 import Template
from jinja2.exceptions import UndefinedError

logger = logging.getLogger(__name__)


class FormUtils:
    @classmethod
    def get_available_fields(cls, job_template_survey, operation_survey, skip_admin_fields=True):
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
            target_tower_field = operation_survey.get(name=survey_filled["variable"])
            if not skip_admin_fields or (skip_admin_fields and target_tower_field.is_customer_field):
                returned_dict["spec"].append(survey_filled)
        return returned_dict

    @classmethod
    def apply_user_validator_to_survey(cls, job_template_survey, operation_survey):
        for survey_filled in job_template_survey.get("spec", []):  # loop all survey config from tower
            target_tower_field = operation_survey.get(name=survey_filled["variable"])
            survey_filled["validators"] = list()
            if target_tower_field.validators is not None:
                survey_filled["validators"] = target_tower_field.validators.split(",")

            # add quota attribute
            survey_filled["quota"] = None
            if target_tower_field.attribute_definition:
                survey_filled["quota"] = target_tower_field.attribute_definition.name
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

    @classmethod
    def get_choices_as_tuples_list(cls, choices, default=None):
        if default is None:
            default = [('', "Select an option")]
        if not isinstance(choices, list):
            choices = choices.splitlines()
        return default + [(choice, choice) for choice in choices]
