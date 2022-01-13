import urllib3
from service_catalog.models import Operation
from service_catalog.models.operations import OperationType
from Squest.utils.squest_model_form import SquestModelForm

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AddServiceOperationForm(SquestModelForm):
    def __init__(self, *args, **kwargs):
        super(AddServiceOperationForm, self).__init__(*args, **kwargs)
        choice_type_others = [('UPDATE', 'Update'),
                              ('DELETE', 'Delete')]

        choice_type_creation = [('CREATE', 'Create')]
        # Default behavior
        self.fields['type'].initial = choice_type_others[0]
        self.fields['type'].choices = choice_type_others

        if self.instance.id:  # if we have an operation
            if self.instance.type == OperationType.CREATE:
                self.fields['type'].initial = choice_type_creation[0]
                self.fields['type'].choices = choice_type_creation

    class Meta:
        model = Operation
        fields = ["name", "description", "job_template", "type", "process_timeout_second",
                  "auto_accept", "auto_process"]
