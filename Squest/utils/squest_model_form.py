
from django.forms import ModelForm, Select, CheckboxInput, CheckboxSelectMultiple, RadioSelect, FileInput


class SquestModelForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(SquestModelForm, self).__init__(*args, **kwargs)
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
            else:
                current_field.widget.attrs['class'] = 'form-control'
