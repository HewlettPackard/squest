from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect

from Squest.utils.squest_views import *
from service_catalog.filters.support_filter import SupportFilter
from service_catalog.models import Support
from service_catalog.tables.support_tables import SupportTable


class SupportListView(SquestListView):
    table_class = SupportTable
    model = Support
    filterset_class = SupportFilter

    def get_queryset(self):
        return Support.get_queryset_for_user(self.request.user, 'service_catalog.view_support')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['html_button_path'] = ""
        return context


class ReOpenSupportView(SquestDetailView):
    model = Support
    permission_required = "service_catalog.reopen_support"

    def dispatch(self, request, *args, **kwargs):
        if request.method != 'GET':
            return HttpResponseNotAllowed(['GET'])
        super(ReOpenSupportView, self).dispatch(request, *args, **kwargs)
        support = self.get_object()
        support.do_open()
        support.save()
        return redirect(support.get_absolute_url())


class CloseSupportView(SquestDetailView):
    model = Support
    permission_required = "service_catalog.close_support"

    def dispatch(self, request, *args, **kwargs):
        if request.method != 'GET':
            return HttpResponseNotAllowed(['GET'])
        super(CloseSupportView, self).dispatch(request, *args, **kwargs)
        support = self.get_object()
        support.do_close()
        support.save()
        return redirect(support.get_absolute_url())
