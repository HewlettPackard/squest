from django.db.models import ManyToManyField, TextField, CharField

from Squest.utils.squest_model import SquestModel


class NotificationFilter(SquestModel):
    class Meta:
        abstract = True

    name = CharField(max_length=100)
    services = ManyToManyField(
        "service_catalog.Service",
        blank=True,
    )
    # "E.G: request.instance.spec['configvar'] == 'value' and request.fill_in_survey['location'] == 'value'"
    when = TextField(blank=True, null=True,
                     help_text="Ansible like 'when' with `request` as context. No Jinja brackets needed")

    def __str__(self):
        return self.name
