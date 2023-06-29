from django.shortcuts import get_object_or_404, redirect
from django.views.generic import RedirectView, DetailView, FormView

from Squest.utils.squest_rbac import SquestPermissionRequiredMixin
from service_catalog.forms import SupportMessageForm
from service_catalog.models import Support


class ReOpenSupportView(SquestPermissionRequiredMixin, DetailView):
    model = Support
    permission_required = "service_catalog.open_support"
    pk_url_kwarg = "support_id"

    def dispatch(self, request, *args, **kwargs):
        super(ReOpenSupportView, self).dispatch(request, *args, **kwargs)
        support = self.get_object()
        support.do_open()
        support.save()
        return redirect(support.get_absolute_url())


class CloseSupportView(SquestPermissionRequiredMixin, DetailView):
    model = Support
    permission_required = "service_catalog.close_support"
    pk_url_kwarg = "support_id"

    def dispatch(self, request, *args, **kwargs):
        super(CloseSupportView, self).dispatch(request, *args, **kwargs)
        support = self.get_object()
        support.do_close()
        support.save()
        return redirect(support.get_absolute_url())
