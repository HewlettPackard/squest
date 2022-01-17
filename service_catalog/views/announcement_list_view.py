from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from guardian.mixins import LoginRequiredMixin

from service_catalog.filters.announcement_filter import AnnouncementFilter
from service_catalog.models import Announcement
from service_catalog.tables.annoucement_tables import AnnouncementTable


@method_decorator(login_required, name='dispatch')
class AnnouncementListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = AnnouncementTable
    model = Announcement
    template_name = 'generics/list.html'
    filterset_class = AnnouncementFilter

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied
        return super(AnnouncementListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Announcements"
        context['html_button_path'] = "generics/buttons/add_announcement.html"
        return context
