from jinja2 import Template, UndefinedError, TemplateSyntaxError


class AnsibleWhen(object):

    @classmethod
    def when_render(cls, context, when_string):
        try:
            template_string = "{% if " + when_string + " %}True{% else %}{% endif %}"
            template = Template(template_string)
        except TemplateSyntaxError:
            return False
        try:
            template_rendered = template.render(context)
            return bool(template_rendered)
        except UndefinedError:
            return False
