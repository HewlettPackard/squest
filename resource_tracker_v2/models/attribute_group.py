from django.db.models import CharField

from Squest.utils.squest_model import SquestModel


class AttributeGroup(SquestModel):
    class Meta(SquestModel.Meta):
        pass

    name = CharField(
        max_length=100,
        blank=False,
        unique=True
    )
    description = CharField(max_length=255, default='', null=True, blank=True)

    def __str__(self):
        return self.name
