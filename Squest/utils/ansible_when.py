from jinja2 import Template, UndefinedError


class AnsibleWhen(object):

    @classmethod
    def when_render(cls, context, when_string):

        template_string = "{% if " + when_string + " %}True{% else %}{% endif %}"
        template = Template(template_string)
        try:
            template_rendered = template.render(context)
            return bool(template_rendered)
        except UndefinedError:
            return False
