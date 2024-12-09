from django.forms import ImageField, FileInput, CharField, ModelChoiceField

from Squest.utils.squest_model_form import SquestModelForm
from profiles.models import Permission
from service_catalog.forms.form_utils import FormUtils
from service_catalog.models.portfolio import Portfolio


class PortfolioForm(SquestModelForm):
    class Meta:
        model = Portfolio
        fields = ["name", "description", "image", "description_doc", "parent_portfolio", "permission"]

    image = ImageField(
        label="Choose a file",
        required=False,
        widget=FileInput()
    )

    permission = ModelChoiceField(
        queryset=Permission.objects.filter(content_type__model="operation", content_type__app_label="service_catalog"),
        initial=FormUtils.get_default_permission_for_operation,
        help_text="Applying a new permission here will apply it on all operations in all sub services")


    def __init__(self, *args, **kwargs):
        super(PortfolioForm, self).__init__(*args, **kwargs)
        if self.instance.id:  # Edit object
            # set permission field. If one operation in the service is not using the default
            all_permission_current_service = Permission.objects.filter(operation__service__in=self.instance.service_list.all()).distinct()
            if all_permission_current_service.count() > 1:
                set_at_operation_level = ('set_at_operation_level','OVERWRITTEN BY OPERATION')
                self.fields["permission"].choices = list(self.fields['permission'].choices) + [set_at_operation_level]
                self.fields["permission"].initial = set_at_operation_level
            else:
                self.fields["permission"].initial = all_permission_current_service.first()


    def save(self, commit=True):
        # save as usual
        obj = super().save(commit)
        # bulk edit on permission
        new_perm = self.cleaned_data.get('permission')
        obj.bulk_set_permission_on_operation(new_perm)
        return obj