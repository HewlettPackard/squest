from profiles.models.organization import Organization
from Squest.utils.squest_filter import SquestFilter


class OrganizationFilter(SquestFilter):
    class Meta:
        model = Organization
        fields = ['name']
