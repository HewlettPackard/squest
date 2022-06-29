from django.db.models import Model, ForeignKey, SET_NULL, CharField, ImageField


class Portfolio(Model):
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



