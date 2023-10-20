from django.contrib.auth.models import User
from Squest.utils.squest_table import SquestRequestConfig

from Squest.utils.squest_views import SquestListView, SquestDetailView
from profiles.filters.user_filter import UserFilter
from profiles.tables.user_table import UserTable
from service_catalog.tables.instance_tables import InstanceTable
from service_catalog.tables.request_tables import RequestTable


class UserListView(SquestListView):
    model = User
    filterset_class = UserFilter
    table_class = UserTable
    app_label = 'profiles'
    ordering = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['html_button_path'] = "profiles/buttons/manage_all_users.html"
        return context


class UserDetailsView(SquestDetailView):
    model = User
    app_label = 'profiles'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = SquestRequestConfig(self.request)

        context['breadcrumbs'] = [
            {
                'text': self.django_content_type.name.capitalize(),
                'url': self.get_generic_url('list')
            },
            {
                'text': f"{self.object.username}",
                'url': ""
            },
        ]

        # Requests
        context['requests'] = RequestTable(self.object.request_set.all(),
                                           hide_fields=["user__username", "instance__service"],
                                           prefix="request-")
        config.configure(context['requests'])
        # Instances
        context['instances'] = InstanceTable(self.object.instance_set.all(),prefix="instance-")
        config.configure(context['instances'])

        return context
