from django_filters import FilterSet, NumberFilter
from django.forms import TextInput, Select, SelectMultiple, CheckboxInput


class SquestFilter(FilterSet):

    def __init__(self, *args, **kwargs):
        super(SquestFilter, self).__init__(*args, **kwargs)

        # Per page at the end of form
        per_page_filter = NumberFilter(
            field_name="per_page",
            label="Number of elements displayed"
        )
        self.filters['per_page'] = per_page_filter
        per_page_filter.field.widget = Select(
            choices=[
                (25, '25'),
                (50, '50'),
                (100, '100'),
                (500, '250'),
                (500, '500'),
                (1000, '1000'),
            ]
        )

        for filter_name, current_filter in self.filters.items():
            if isinstance(current_filter.field.widget, TextInput):
                current_filter.field.widget.attrs['class'] = 'form-control'
                current_filter.lookup_expr = 'icontains'
                if self.request and '/api/' in self.request.path:
                    current_filter.lookup_expr = 'exact'
            elif isinstance(current_filter.field.widget, Select) or isinstance(current_filter.field.widget,
                                                                               SelectMultiple):
                current_filter.field.widget.attrs['class'] = 'form-control selectpicker'
                current_filter.field.widget.attrs['data-live-search'] = 'true'
            elif isinstance(current_filter.field.widget, CheckboxInput):
                current_filter.field.widget.attrs['class'] = 'form-control-checkbox'
            else:
                current_filter.field.widget.attrs['class'] = 'form-control'

    def fake_filter_method(self, queryset, name, value):
        return queryset

    def filter_queryset(self, queryset):
        self.form.cleaned_data.pop("per_page")
        return super().filter_queryset(queryset)
