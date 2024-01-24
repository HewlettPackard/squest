from django.db.models import CharField, ManyToManyField
from jinja2 import Template, UndefinedError, TemplateSyntaxError, TemplateError
from martor.models import MartorField

from Squest.utils.squest_model import SquestModel

import logging

logger = logging.getLogger(__name__)


class Doc(SquestModel):
    title = CharField(max_length=100)
    content = MartorField()
    services = ManyToManyField(
        'service_catalog.Service',
        blank=True,
        help_text="Services linked to this doc.",
        related_name="docs",
        related_query_name="doc",
    )
    operations = ManyToManyField(
        'service_catalog.Operation',
        blank=True,
        help_text="Operations linked to this doc.",
        related_name="docs",
        related_query_name="doc",
    )
    when = CharField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return self.title

    def render(self, instance=None):
        if instance is None:
            return self.content
        try:
            template = Template(self.content)
            context = {
                "instance": instance
            }
            return template.render(context)
        except UndefinedError as e:
            logger.warning(f"Error: {e.message}, instance: {instance}, doc: {self}")
            raise TemplateError(e)
        except TemplateSyntaxError as e:
            logger.warning(f"Error: {e.message}, instance: {instance}, doc: {self}")
            raise TemplateError(e)
        except TypeError as e:
            logger.warning(f"Error: {e}, instance: {instance}, doc: {self}")
            raise TemplateError(e)
