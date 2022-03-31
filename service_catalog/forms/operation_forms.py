from service_catalog.models import Operation
from service_catalog.models.operations import OperationType
from Squest.utils.squest_model_form import SquestModelForm


class ServiceOperationForm(SquestModelForm):
    def __init__(self, *args, **kwargs):
        self.service = kwargs.pop("service")
        super(ServiceOperationForm, self).__init__(*args, **kwargs)
        choice_type_others = [('UPDATE', 'Update'),
                              ('DELETE', 'Delete')]
        choice_type_creation = [('CREATE', 'Create')]
        # Default behavior
        self.fields['type'].choices = choice_type_others
        if not self.service.operations.filter(type=OperationType.CREATE).exists() or (self.instance.id and self.instance.type == OperationType.CREATE):
            self.fields['type'].choices = [*choice_type_creation, *choice_type_others]
        self.fields['type'].initial = self.fields['type'].choices[0]

    def save(self, commit=True):
        new_operation = super(ServiceOperationForm, self).save(commit=False)
        new_operation.service = self.service
        new_operation.save()

    class Meta:
        model = Operation
        fields = ["name", "description", "job_template", "type", "process_timeout_second", "auto_accept",
                  "auto_process", "enabled"]
