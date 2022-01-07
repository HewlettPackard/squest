from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django.contrib.auth.models import Group
from guardian.mixins import LoginRequiredMixin

from profiles.filters.group_filter import GroupFilter
from profiles.tables.group_table import GroupTable


@method_decorator(login_required, name='dispatch')
class GroupListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = GroupTable
    model = Group
    template_name = 'generics/list.html'
    filterset_class = GroupFilter

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied
        return super(GroupListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Groups"
        context['html_button_path'] = "generics/buttons/add_group.html"
        context['object_name'] = 'group'
        return context
