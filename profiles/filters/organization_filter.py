from Squest.utils.squest_filter import SquestFilter
from profiles.models.organization import Organization


class OrganizationFilter(SquestFilter):
    class Meta:
        model = Organization
        fields = ['name']
