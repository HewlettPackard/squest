from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import tables, TemplateColumn, Column
from guardian.mixins import LoginRequiredMixin

from service_catalog.filters.announcement_filter import AnnouncementFilter
from service_catalog.models import Announcement


class AnnouncementTable(tables.Table):
    actions = TemplateColumn(template_name='custom_columns/announcement_actions.html', orderable=False)
    type = TemplateColumn(template_name='custom_columns/announcement_type.html')
    created_by__username = Column(verbose_name='Owner')

    class Meta:
        model = Announcement
        attrs = {"id": "announcement_table", "class": "table squest-pagination-tables"}
        fields = ("title", "date_start", "date_stop", "created_by__username", "type", "actions")


class AnnouncementListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = AnnouncementTable
    model = Announcement
    template_name = 'generics/list.html'
    filterset_class = AnnouncementFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Announcements"
        context['html_button_path'] = "generics/buttons/add_announcement.html"
        return context
