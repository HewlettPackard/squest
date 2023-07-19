from Squest.utils.squest_views import *
from service_catalog.filters.custom_link_filter import CustomLinkFilter
from service_catalog.forms.custom_link_form import CustomLinkForm
from service_catalog.models import CustomLink
from service_catalog.tables.custom_link_table import CustomLinkTable


class CustomLinkListView(SquestListView):
    table_class = CustomLinkTable
    model = CustomLink
    filterset_class = CustomLinkFilter


class CustomLinkCreateView(SquestCreateView):
    model = CustomLink
    form_class = CustomLinkForm


class CustomLinkEditView(SquestUpdateView):
    model = CustomLink
    form_class = CustomLinkForm


class CustomLinkDeleteView(SquestDeleteView):
    model = CustomLink
    template_name = 'generics/confirm-delete-template.html'
