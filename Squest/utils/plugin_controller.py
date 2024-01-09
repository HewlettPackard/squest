import logging
from importlib.machinery import SourceFileLoader
import inspect
import os
from pydoc import locate
import re

from django.conf import settings

VALIDATE_UI_DEFINITION_NAME = "validate_ui"
VALIDATE_API_DEFINITION_NAME = "validate_api"

logger = logging.getLogger(__name__)


def full_path_to_dotted_path(path):
    # /foo/bar/myfile.py -> foo.bar.myfile
    path = re.sub(r"\.py", "", path)
    path = re.sub(r"/", ".", path)
    return path

class PluginController:

    @classmethod
    def get_user_provisioned_field_validators(cls):
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
    def get_user_provisioned_survey_validators(cls):
        def is_validator(obj):
            """
            Returns True if the object is a Script.
            """
            from service_catalog.forms import SurveyValidator
            try:
                return issubclass(obj, SurveyValidator) and obj != SurveyValidator
            except TypeError:
                return False

        def python_name(full_path):
            # /foo/bar/myfile.py -> myfile
            path, filename = os.path.split(full_path)
            name = os.path.splitext(filename)[0]
            if name == "__init__":
                # File is a package
                return os.path.basename(path)
            else:
                return name

        scripts = list()
        for filename in os.listdir(settings.SURVEY_VALIDATOR_PATH):
            if filename in ["__init__.py", "__pycache__"]:
                continue
            full_path = os.path.join(settings.SURVEY_VALIDATOR_PATH, filename)
            loader = SourceFileLoader(python_name(filename), full_path)
            module = loader.load_module()
            for name, klass in inspect.getmembers(module, is_validator):
                dotted_path = f"{python_name(filename)}.{klass.__name__}"
                scripts.append(dotted_path)
        return scripts

    @classmethod
    def get_ui_field_validator_def(cls, validator_file):
        return cls._load_field_validator_module(module_name=validator_file, definition_kind=VALIDATE_UI_DEFINITION_NAME)

    @classmethod
    def get_api_field_validator_def(cls, validator_file):
        return cls._load_field_validator_module(module_name=validator_file,
                                                definition_kind=VALIDATE_API_DEFINITION_NAME)

    @classmethod
    def get_survey_validator_def(cls, validator_path):
        return locate(f"{full_path_to_dotted_path(settings.SURVEY_VALIDATOR_PATH)}.{validator_path}")

    @classmethod
    def _load_field_validator_module(cls, module_name, definition_kind):
        logger.warning("Deprecation warning: Please switch to SurveyValidator")
        filepath = settings.FIELD_VALIDATOR_PATH
        return cls._load_validator_module(module_name, definition_kind, filepath)

    @staticmethod
    def _load_validator_module(module_name, definition_kind, filepath):
        """
        Dynamically load a validator definition from a python file
        :param module_name: name of the python file that contains validator definitions
        :param definition_kind: UI or API
        :return:
        """
        try:
            mod = __import__(f"{filepath.replace('/', '.')}.{module_name}",
                             fromlist=[definition_kind])
            klass = getattr(mod, definition_kind)
            return klass
        except ModuleNotFoundError:
            logger.warning(f"[PluginController] Validator file not loaded: {module_name}."
                           f" Check that the file exists in the plugin directory.")
            return None
