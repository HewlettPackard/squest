import logging

from jinja2 import Template, UndefinedError, TemplateSyntaxError

logger = logging.getLogger(__name__)

class AnsibleWhen(object):

    @classmethod
    def when_render(cls, context, when_string):
        if when_string is None or when_string == "" or context is None:
            return False
        template_string = "{% if " + when_string + " %}True{% else %}{% endif %}"
        try:
            template = Template(template_string)
        except TemplateSyntaxError:
            logger.warning(f"when_render error when templating: {context} with string '{when_string}'")
            return False
        try:
            template_rendered = template.render(context)
            return bool(template_rendered)
        except UndefinedError:
            logger.warning(f"when_render error when templating: {context} with string '{when_string}'")
            return False
