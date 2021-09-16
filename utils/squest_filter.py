import django_filters
from django import forms


class SquestFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        super(SquestFilter, self).__init__(*args, **kwargs)
        for filter_name, current_filter in self.filters.items():
            if isinstance(current_filter.field.widget, forms.TextInput):
                current_filter.field.widget.attrs['class'] = 'form-control'
                current_filter.lookup_expr = 'icontains'
            elif isinstance(current_filter.field.widget, forms.Select):
                current_filter.field.widget.attrs['class'] = 'form-control selectpicker'
            elif isinstance(current_filter.field.widget, forms.CheckboxInput):
                current_filter.field.widget.attrs['class'] = 'form-control-checkbox'
            else:
                current_filter.field.widget.attrs['class'] = 'form-control'
