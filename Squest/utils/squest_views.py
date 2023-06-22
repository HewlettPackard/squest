from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin


class SquestListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content_type = ContentType.objects.get_for_model(self.model)
        context['title'] = content_type.name.capitalize()
        context['app_name'] = content_type.app_label
        context['object_name'] = content_type.model
        return context
