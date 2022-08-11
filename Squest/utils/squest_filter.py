import django_filters
from django.forms import TextInput, Select, SelectMultiple, CheckboxInput


class SquestFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        super(SquestFilter, self).__init__(*args, **kwargs)
        for filter_name, current_filter in self.filters.items():
            if isinstance(current_filter.field.widget, TextInput):
                current_filter.field.widget.attrs['class'] = 'form-control'
                current_filter.lookup_expr = 'icontains'
                if self.request and '/api/' in self.request.path:
                    current_filter.lookup_expr = 'exact'
            elif isinstance(current_filter.field.widget, Select) or isinstance(current_filter.field.widget, SelectMultiple):
                current_filter.field.widget.attrs['class'] = 'form-control selectpicker'
                current_filter.field.widget.attrs['data-live-search'] = 'true'
            elif isinstance(current_filter.field.widget, CheckboxInput):
                current_filter.field.widget.attrs['class'] = 'form-control-checkbox'
            else:
                current_filter.field.widget.attrs['class'] = 'form-control'
