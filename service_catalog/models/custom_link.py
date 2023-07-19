from django.db.models import CharField, ManyToManyField, BooleanField, TextChoices
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from Squest.utils.squest_model import SquestModel
from . import Service


class LinkButtonClassChoices(TextChoices):

    DEFAULT = 'default', _('Default')
    BLUE = 'primary', _('Blue')
    GRAY = 'secondary', _('Gray')
    GREEN = 'success', _('Green')
    RED = 'danger', _('Red')
    YELLOW = 'warning', _('Yellow')
    CYAN = 'info', _('Cyan')
    LIGHT = 'light', _('Light')
    DARK = 'dark', _('Dark')
    LINK = 'link', _('Link')


class CustomLink(SquestModel):

    class Meta:
        permissions = [
            ("view_admin_customlink", "Can view admin custom link"),
        ]
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    name = CharField(max_length=100)
    text = CharField(max_length=250)
    url = CharField(max_length=2000)
    button_class = CharField(
        max_length=30,
        choices=LinkButtonClassChoices.choices,
        default=LinkButtonClassChoices.DEFAULT,
        verbose_name="Button color"
    )
    when = CharField(max_length=2000, blank=True, null=True)
    is_admin_only = BooleanField(default=False, help_text='If "is admin only" then permission service_catalog.view_admin_custom_link is required to see it in your instances')
    enabled = BooleanField(default=True)
    loop = CharField(max_length=2000, blank=True)  # {{  instance.spec.my_list }}

    services = ManyToManyField(
        Service,
        blank=True,
        help_text="Services linked to this custom link.",
        related_name="custom_links",
        related_query_name="custom_link",
    )

    def get_absolute_url(self):
        return reverse("service_catalog:customlink_list")

    def __str__(self):
        return f"{self.name} ({','.join(self.services.all().values_list('name', flat=True))})"
