import logging

from django import forms
from django.forms import CharField, TextInput, ChoiceField, MultipleChoiceField
from jinja2 import TemplateSyntaxError

from service_catalog.api.serializers import RequestSerializer
from service_catalog.forms.form_utils import FormUtils
from service_catalog.utils import str_to_bool

logger = logging.getLogger(__name__)


class ProcessRequestForm(forms.Form):

    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.target_request = kwargs.pop('request', None)
        super(ProcessRequestForm, self).__init__(*args, **kwargs)
        self.fields.update(self.get_job_template_fields())

    def get_job_template_fields(self):
        fields = dict()
        if self.remote_job_template_data_key_enabled("ask_job_type_on_launch"):
            fields["ask_job_type_on_launch"] = self._get_job_type_field()
        if self.remote_job_template_data_key_enabled("ask_limit_on_launch"):
            fields["ask_limit_on_launch"] = self._get_limit_field()
        if self.remote_job_template_data_key_enabled("ask_tags_on_launch"):
            fields["ask_tags_on_launch"] = self._get_tags_field()
        if self.remote_job_template_data_key_enabled("ask_skip_tags_on_launch"):
            fields["ask_skip_tags_on_launch"] = self._get_skip_tags_field()
        if self.remote_job_template_data_key_enabled("ask_inventory_on_launch"):
            fields["ask_inventory_on_launch"] = self._get_inventory_field()
        if self.remote_job_template_data_key_enabled("ask_credential_on_launch"):
            fields["ask_credential_on_launch"] = self._get_credentials_field()
        if self.remote_job_template_data_key_enabled("ask_verbosity_on_launch"):
            fields["ask_verbosity_on_launch"] = self._get_verbosity_field()
        if self.remote_job_template_data_key_enabled("ask_diff_mode_on_launch"):
            fields["ask_diff_mode_on_launch"] = self._get_diff_mode_field()
        return fields

    def remote_job_template_data_key_enabled(self, key_to_find):
        if key_to_find in self.target_request.operation.job_template.remote_job_template_data:
            return str_to_bool(self.target_request.operation.job_template.remote_job_template_data[key_to_find])
        return False

    def _get_job_type_field(self):
        initial = "run"
        try:
            initial = self.target_request.operation.job_template.remote_job_template_data["job_type"]
        except KeyError:
            pass
        if self.target_request.operation.default_job_type is not None \
                and self.target_request.operation.default_job_type != "":
            initial = self._get_templated_initial(self.target_request.operation.default_job_type)
        choices = [("run", "Run"), ("check", "Check")]
        return ChoiceField(
            label="Job Type",
            initial=initial,
            required=False,
            help_text="",
            choices=choices,
            widget=forms.Select(attrs={"class": "form-control selectpicker", "data-live-search": "true"})
        )

    def _get_diff_mode_field(self):
        initial = False
        try:
            initial = self.target_request.operation.job_template.remote_job_template_data["diff_mode"]
            initial = str_to_bool(initial)
        except KeyError:
            pass
        if self.target_request.operation.default_diff_mode is not None \
                and self.target_request.operation.default_diff_mode != "":
            initial = self._get_templated_initial(self.target_request.operation.default_diff_mode)
        choices = [(False, "False"), (True, "True")]
        return ChoiceField(
            label="Diff mode",
            initial=initial,
            required=False,
            help_text="",
            choices=choices,
            widget=forms.Select(attrs={"class": "form-control selectpicker", "data-live-search": "true"})
        )

    def _get_limit_field(self):
        initial = ""
        try:
            initial = self.target_request.operation.job_template.remote_job_template_data["limit"]
        except KeyError:
            pass
        if self.target_request.operation.default_limits is not None and self.target_request.operation.default_limits != "":
            initial = self._get_templated_initial(self.target_request.operation.default_limits)
        return CharField(
            label="Limit",
            initial=initial,
            required=False,
            help_text="",
            widget=TextInput(
                attrs={'class': 'form-control'}
            )
        )

    def _get_tags_field(self):
        initial = ""
        try:
            initial = self.target_request.operation.job_template.remote_job_template_data["job_tags"]
        except KeyError:
            pass
        if self.target_request.operation.default_tags is not None and self.target_request.operation.default_tags != "":
            initial = self._get_templated_initial(self.target_request.operation.default_tags)
        return CharField(
            label="Tags",
            initial=initial,
            required=False,
            help_text="",
            widget=TextInput(
                attrs={'class': 'form-control'}
            )
        )

    def _get_skip_tags_field(self):
        initial = ""
        try:
            initial = self.target_request.operation.job_template.remote_job_template_data["skip_tags"]
        except KeyError:
            pass
        if self.target_request.operation.default_skip_tags is not None and self.target_request.operation.default_skip_tags != "":
            initial = self._get_templated_initial(self.target_request.operation.default_skip_tags)
        return CharField(
            label="Skip Tags",
            initial=initial,
            required=False,
            help_text="",
            widget=TextInput(
                attrs={'class': 'form-control'}
            )
        )

    def _get_inventory_field(self):
        initial = ""
        try:
            initial = self.target_request.operation.job_template.remote_job_template_data["summary_fields"]["inventory"]["id"]
        except KeyError:
            pass
        if self.target_request.operation.default_inventory_id is not None and self.target_request.operation.default_inventory_id != "":
            initial = self._get_templated_initial(self.target_request.operation.default_inventory_id)
        return ChoiceField(
            label="Inventory",
            initial=initial,
            required=False,
            help_text="",
            choices=self.get_inventories_as_choices(),
            widget=forms.Select(attrs={"class": "form-control selectpicker", "data-live-search": "true"})
        )

    def _get_verbosity_field(self):
        initial = 0
        try:
            initial = self.target_request.operation.job_template.remote_job_template_data["verbosity"]
        except KeyError:
            pass
        if self.target_request.operation.default_verbosity is not None \
                and self.target_request.operation.default_verbosity != "":
            initial = self._get_templated_initial(self.target_request.operation.default_verbosity)
        choices = [(0, "0 (Normal)"), (1, "1 (Verbose)"),
                   (2, "1 (More verbose)"), (3, "3 (Debug)"), (4, "4 (Connection Debug)")]
        return ChoiceField(
            label="Verbosity",
            initial=initial,
            required=False,
            help_text="",
            choices=choices,
            widget=forms.Select(attrs={"class": "form-control selectpicker", "data-live-search": "true"})
        )

    def _get_credentials_field(self):
        initial = []
        try:
            credentials = self.target_request.operation.job_template.remote_job_template_data["summary_fields"]["credentials"]
            for credential in credentials:
                initial.append(str(credential["id"]))
        except KeyError:
            pass
        if self.target_request.operation.default_credentials_ids is not None and self.target_request.operation.default_credentials_ids != "":
            credential_initial = self._get_templated_initial(self.target_request.operation.default_credentials_ids)
            if credential_initial is not None:
                initial = credential_initial.split(",")
        return MultipleChoiceField(
            label="Credentials",
            initial=initial,
            required=False,
            help_text="",
            choices=self.get_credentials_as_choices(),
            widget=forms.SelectMultiple(attrs={"class": "form-control selectpicker", "data-live-search": "true"})
        )

    def is_all_field_visible_to_admin_or_user_only(self):
        """
        Return True if all field of the tower survey are visible only to the end user or only to admin
        """
        all_fields_for_admin = self.target_request.operation.survey_fields.filter(
            is_customer_field=False).count() == self.target_request.operation.survey_fields.all().count()
        all_fields_for_user = self.target_request.operation.survey_fields.filter(
            is_customer_field=True).count() == self.target_request.operation.survey_fields.all().count()
        return all_fields_for_admin or all_fields_for_user

    def _get_templated_initial(self, jinja_string):
        context = {
            "request": RequestSerializer(self.target_request).data
        }
        try:
            templated_string = FormUtils.template_field(jinja_string, context) if jinja_string is not None else None
        except TemplateSyntaxError as e:
            logger.warning(f"[_get_templated_initial] fail to template string '{jinja_string}': {e.message}")
            return ""
        return templated_string

    def get_inventories_as_choices(self):
        choices = list()
        for inventory in self.target_request.operation.job_template.ansible_controller.inventories.all():
            choices.append((inventory.ansible_controller_id, inventory.name))
        return choices

    def get_credentials_as_choices(self):
        choices = list()
        for credential in self.target_request.operation.job_template.ansible_controller.credentials.all():
            choices.append((credential.ansible_controller_id, credential.name))
        return choices
