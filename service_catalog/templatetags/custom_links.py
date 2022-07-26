import ast
import logging

from django import template as django_template
from django.utils.safestring import mark_safe
from jinja2 import Template, UndefinedError

from Squest.utils.ansible_when import AnsibleWhen
from service_catalog.models import CustomLink

register = django_template.Library()

logger = logging.getLogger(__name__)


def get_disabled_button(tittle, button_name):
    return f'<a class="btn btn-sm btn-outline-dark ml-1" disabled="disabled" title="{tittle}">' \
                                     f'<i class="fas fa-exclamation-triangle"></i> {button_name}</a>\n'


@register.simple_tag
def custom_links(user, instance):

    rendered_buttons = ""

    for custom_link in CustomLink.objects.filter(services=instance.service):

        if custom_link.enabled and (not custom_link.is_admin_only or (custom_link.is_admin_only and user.is_superuser)):
            # prepare a context for jinja templating
            context = {
                "instance": instance,
            }

            # check the when
            if custom_link.when:
                if not AnsibleWhen.when_render(context=context, when_string=custom_link.when):
                    continue

            if custom_link.loop:
                # set button as dropdown button
                rendered_buttons += get_dropdown_button(custom_link=custom_link, context=context)
            else:
                # single button
                rendered_buttons += get_single_button(custom_link=custom_link, context=context)

    return mark_safe(rendered_buttons)


def get_single_button(custom_link, context):
    try:
        template_url = Template(custom_link.url)
        rendered_url = template_url.render(context)
        template_text = Template(custom_link.text)
        rendered_text = template_text.render(context)
    except UndefinedError as e:
        # in case of any error we skip the button generation
        logger.warning(f"[custom_links] failed to render: {e.message}")
        return get_disabled_button(tittle=e, button_name=custom_link.name)

    templated_button = f"<a href=\"{rendered_url}\" class=\"btn btn-sm btn-{custom_link.button_class} ml-1\">{rendered_text}</a>"
    return templated_button


def get_dropdown_button(custom_link, context):
    # get object from the loop
    template_loop = Template(custom_link.loop)
    rendered_loop = template_loop.render(context)
    try:
        iterable_loop = ast.literal_eval(rendered_loop)
    except Exception as e:
        logger.warning(f"[custom_links] failed to render: {e}")
        return get_disabled_button(tittle=e, button_name=custom_link.name)

    # prepare each link od the dropdown menu
    list_li_group_link = list()
    for item in iterable_loop:
        context_with_item = {
            "item": item,
            "instance": context["instance"]
        }
        try:
            template_url = Template(custom_link.url)
            rendered_url = template_url.render(context_with_item)
            template_text = Template(custom_link.text)
            rendered_text = template_text.render(context_with_item)
        except UndefinedError as e:
            # in case of any error we skip the button generation
            logger.warning(f"[custom_links] failed to render: {e.message}")
            return get_disabled_button(tittle=e.message, button_name=custom_link.name)
        li_group_link = f"<a class=\"dropdown-item\" href=\"{rendered_url}\">{rendered_text}</a>\n"
        list_li_group_link.append(li_group_link)

    # prepare the main button
    dropdown_button = """
        <div class="dropdown">
        <button class="btn btn-sm btn-{{ custom_link.button_class }} 
            dropdown-toggle ml-1" 
            type="button" 
            id="dropdown-{{ custom_link.id }}" 
            data-toggle="dropdown" 
            aria-haspopup="true" 
            aria-expanded="false">
        {{ custom_link.name }}    
        </button>
        <div class="dropdown-menu" aria-labelledby="dropdownMenuButton">
            {% for li_item in list_li_group_link %}
                {{ li_item }}
            {% endfor %}
        </div>
        </div>
        """
    dropdown_context = {
        "custom_link": custom_link,
        "list_li_group_link": list_li_group_link
    }
    templated_dropdown = Template(dropdown_button)
    rendered_dropdown = templated_dropdown.render(dropdown_context)
    return rendered_dropdown
