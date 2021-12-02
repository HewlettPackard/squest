from django.contrib.auth.models import Group
from Squest.utils.squest_filter import SquestFilter


class GroupFilter(SquestFilter):
    class Meta:
        model = Group
        fields = ['name']
