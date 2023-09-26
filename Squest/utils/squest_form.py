
from django.forms import Select, CheckboxInput, CheckboxSelectMultiple, RadioSelect, FileInput, DateTimeInput, Form
from django.utils import timezone
from tempus_dominus.widgets import DateTimePicker


class SquestForm(Form):

    help_text = None
    error_css_class = 'is-invalid'

    def __init__(self, *args, **kwargs):
        super(SquestForm, self).__init__(*args, **kwargs)
        self.beautify()

    def is_valid(self):
        returned_value = super(SquestForm, self).is_valid()
        for field_name in self.errors.keys():
            current_class = self.fields.get(field_name).widget.attrs.get('class', '')
            self.fields.get(field_name).widget.attrs['class'] = f"{current_class} {self.error_css_class}"
        return returned_value

    def beautify(self):
        for field_name, current_field in self.fields.items():
            if isinstance(current_field.widget, Select):
                current_field.widget.attrs['class'] = 'form-control selectpicker'
                current_field.widget.attrs['data-live-search'] = "true"
            elif isinstance(current_field.widget, CheckboxInput):
                current_field.widget.attrs['class'] = ''
            elif isinstance(current_field.widget, CheckboxSelectMultiple):
                current_field.widget.attrs['class'] = 'form-control form-control-checkbox disable_list_style'
            elif isinstance(current_field.widget, RadioSelect):
                current_field.widget.attrs['class'] = "disable_list_style"
            elif isinstance(current_field.widget, FileInput):
                current_field.widget.attrs['class'] = ""
            elif isinstance(current_field.widget, DateTimeInput):
                current_field.widget = DateTimePicker(
                    options={
                        'timeZone': str(timezone.get_current_timezone()),
                        'collapse': False,
                    }, attrs={
                        'append': 'fa fa-calendar',
                        'icon_toggle': True,
                    }
                )
            else:
                current_field.widget.attrs['class'] = 'form-control'
