import copy
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
        if "spec" in job_template_survey:
            for survey_filed in job_template_survey["spec"]:
                if operation_survey.get(name=survey_filed["variable"]).enabled:
                    returned_dict["spec"].append(survey_filed)
        return returned_dict
