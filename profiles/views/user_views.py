from Squest.utils.squest_views import SquestListView
from profiles.filters.user_filter import UserFilter
from profiles.tables.user_table import UserTable
from django.contrib.auth.models import User
from django.urls import reverse
from django.views.generic import DetailView

from service_catalog.tables.instance_tables import InstanceTable
from service_catalog.tables.request_tables import RequestTable




class UserListView(SquestListView):
    table_pagination = {'per_page': 10}
    table_class = UserTable
    model = User
    template_name = 'generics/list.html'
    filterset_class = UserFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['html_button_path'] = "generics/buttons/manage_all_users.html"
        return context


class UserDetailsView(DetailView):
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Breadcrumbs
        breadcrumbs = [
            {'text': 'Users', 'url': reverse('profiles:user_list')},
            {'text': f'{self.object}', 'url': ""},
        ]
        context['breadcrumbs'] = breadcrumbs

        # Requests
        context['requests'] = RequestTable(self.object.request_set.all())

        # Instances
        context['instances'] = InstanceTable(self.object.instance_set.all())


        return context
