from django.utils import timezone
from Squest.utils.squest_views import *
from service_catalog.filters.announcement_filter import AnnouncementFilter
from service_catalog.forms import AnnouncementForm
from service_catalog.models import Announcement
from service_catalog.tables.annoucement_tables import AnnouncementTable


class AnnouncementListView(SquestListView):
    table_class = AnnouncementTable
    model = Announcement
    filterset_class = AnnouncementFilter


class AnnouncementCreateView(SquestCreateView):
    model = Announcement
    form_class = AnnouncementForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class AnnouncementEditView(SquestUpdateView):
    model = Announcement
    form_class = AnnouncementForm


class AnnouncementDeleteView(SquestDeleteView):
    model = Announcement

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['details'] = {
            'warning_sentence': 'Warning: this announcement is displayed',
            'details_list': None
        } if self.object.date_start < timezone.now() < self.object.date_stop else None
        return context
