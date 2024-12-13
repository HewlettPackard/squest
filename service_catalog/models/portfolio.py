import logging

from django.db.models import ForeignKey, SET_NULL, CharField, ImageField
from django.urls import reverse_lazy

from Squest.utils.squest_model import SquestModel
from profiles.models import Permission

logger = logging.getLogger(__name__)

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

    def bulk_set_permission_on_operation(self, target_permission):
        from service_catalog.models import Operation
        logger.debug(f"Bulk edit permission on portfolio {self.name} to permission {target_permission}")
        # check if all permission are already set to the target perm
        all_permission_current_portfolio = Permission.objects.filter(operation__service__parent_portfolio=self).distinct()
        # if the target perm is already the one used we do nothing
        if all_permission_current_portfolio.count() == 1:
            if all_permission_current_portfolio.first() == target_permission:
                return
        Operation.objects.filter(service__parent_portfolio=self).update(permission=target_permission)