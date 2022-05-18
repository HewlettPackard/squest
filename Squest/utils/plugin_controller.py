import logging
import os

from django.conf import settings

VALIDATE_UI_DEFINITION_NAME = "validate_ui"
VALIDATE_API_DEFINITION_NAME = "validate_api"

logger = logging.getLogger(__name__)


class PluginController:

    @classmethod
    def get_user_provisioned_validators(cls):
        filepath = settings.FIELD_VALIDATOR_PATH
        file_list = os.listdir(filepath)
        for forbidden_word in ["__init__.py", "__pycache__"]:
            if forbidden_word in file_list:
                file_list.remove(forbidden_word)
        returned_list = list()
        for file_name in file_list:
            returned_list.append(os.path.splitext(file_name)[0])
        returned_list.sort()
        return returned_list

    @classmethod
    def get_ui_field_validator_def(cls, validator_file):
        return cls._load_validator_module(module_name=validator_file, definition_kind=VALIDATE_UI_DEFINITION_NAME)

    @classmethod
    def get_api_field_validator_def(cls, validator_file):
        return cls._load_validator_module(module_name=validator_file, definition_kind=VALIDATE_API_DEFINITION_NAME)

    @classmethod
    def _load_validator_module(cls, module_name, definition_kind):
        """
        Dynamically load a validator definition from a python file
        :param module_name: name of the python file that contains field validator definitions
        :param definition_kind: UI or API
        :return:
        """
        try:
            mod = __import__(f"{settings.FIELD_VALIDATOR_PATH.replace('/','.')}.{module_name}",
                             fromlist=[definition_kind])
            klass = getattr(mod, definition_kind)
            return klass
        except ModuleNotFoundError:
            logger.warning(f"[PluginController] Validator file not loaded: {module_name}."
                           f" Check that the file exists in the plugin directory.")
            return None
