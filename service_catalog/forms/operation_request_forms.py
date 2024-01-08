from django import forms

from Squest.utils.squest_form import SquestForm
from service_catalog.forms.form_generator import FormGenerator
from service_catalog.models import Request, RequestMessage

EXCLUDED_SURVEY_FIELDS = ["request_comment"]


class OperationRequestForm(SquestForm):
    request_comment = forms.CharField(label="Comment",
                                      help_text="Add a comment to your request",
                                      widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
                                      required=False)

    def __init__(self, user, *args, **kwargs):
        # get arguments from instance
        self.user = user
        self.operation = kwargs.pop('operation', None)
        self.instance = kwargs.pop('instance', None)
        super(OperationRequestForm, self).__init__(*args, **kwargs)
        form_generator = FormGenerator(user=self.user, operation=self.operation, squest_instance=self.instance)
        self.fields.update(form_generator.generate_form())

    def save(self):
        user_provided_survey_fields = dict()
        for field_key, value in self.cleaned_data.items():
            if field_key not in EXCLUDED_SURVEY_FIELDS:
                user_provided_survey_fields[field_key] = value
        new_request = Request.objects.create(instance=self.instance,
                                             operation=self.operation,
                                             fill_in_survey=user_provided_survey_fields,
                                             user=self.user)

        # save the comment
        request_comment = self.cleaned_data["request_comment"] if self.cleaned_data["request_comment"] else None
        message = None
        if request_comment is not None:
            message = RequestMessage.objects.create(request=new_request, sender=self.user, content=request_comment)
        from service_catalog.mail_utils import send_mail_request_update
        send_mail_request_update(target_request=new_request, user_applied_state=new_request.user, message=message)
        return new_request

    def clean(self):
        super().clean()
        for validators in self.operation.get_validators():
            # load dynamically the user provided validator
            validators(
                survey=self.cleaned_data,
                user=self.user,
                operation=self.operation,
                instance=self.instance,
                form=self
            )._validate()
        return self.cleaned_data
