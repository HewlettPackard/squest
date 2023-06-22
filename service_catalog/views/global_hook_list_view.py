from django.core.exceptions import PermissionDenied

from Squest.utils.squest_views import SquestListView
from service_catalog.filters.global_hook_filter import GlobalHookFilter
from service_catalog.models import GlobalHook
from service_catalog.tables.global_hook_tables import GlobalHookTable


class GlobalHookListView(SquestListView):
    table_pagination = {'per_page': 10}
    table_class = GlobalHookTable
    model = GlobalHook
    template_name = 'generics/list.html'
    filterset_class = GlobalHookFilter

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied
        return super(GlobalHookListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['html_button_path'] = "generics/buttons/create_global_hook.html"
        return context
