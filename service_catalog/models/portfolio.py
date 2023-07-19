from django.db.models import ForeignKey, SET_NULL, CharField, ImageField
from django.urls import reverse_lazy

from Squest.utils.squest_model import SquestModel


class Portfolio(SquestModel):
    name = CharField(max_length=100)
    description = CharField(max_length=500, blank=True)
    image = ImageField(upload_to='portfolio_image', blank=True)
    parent_portfolio = ForeignKey(
        "service_catalog.Portfolio",
        blank=True,
        null=True,
        on_delete=SET_NULL,
        related_name="portfolio_list",
        related_query_name="portfolio_list",
    )
    description_doc = ForeignKey('service_catalog.Doc', blank=True, null=True, on_delete=SET_NULL,
                                 verbose_name='Description documentation')

    def get_absolute_url(self):
        return reverse_lazy("service_catalog:portfolio_list")

    def __str__(self):
        return self.name

    def get_parents(self):
        if not self.parent_portfolio:
            return [self]
        return self.parent_portfolio.get_parents() + [self]

    def delete(self, using=None, keep_parents=False):
        self.portfolio_list.update(**{"parent_portfolio": self.parent_portfolio})
        self.service_list.update(**{"parent_portfolio": self.parent_portfolio})
        super(Portfolio, self).delete(using, keep_parents)
