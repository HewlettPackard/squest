from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404

from Squest.utils.squest_views import *
from service_catalog.filters.email_template_filter import EmailTemplateFilter
from service_catalog.forms.email_template_form import EmailTemplateForm, EmailTemplateSendForm
from service_catalog.models import EmailTemplate
from service_catalog.tables.email_template_table import EmailTemplateTable


class EmailTemplateListView(SquestListView):
    table_class = EmailTemplateTable
    model = EmailTemplate
    filterset_class = EmailTemplateFilter


class EmailTemplateDetailView(SquestDetailView):
    model = EmailTemplate


class EmailTemplateCreateView(SquestCreateView):
    model = EmailTemplate
    form_class = EmailTemplateForm


class EmailTemplateEditView(SquestUpdateView):
    model = EmailTemplate
    form_class = EmailTemplateForm


class EmailTemplateDeleteView(SquestDeleteView):
    model = EmailTemplate


class EmailTemplateSend(SuccessMessageMixin, SquestFormView):
    template_name = 'generics/generic_form.html'
    form_class = EmailTemplateSendForm
    model = EmailTemplate

    def get_success_message(self, cleaned_data):
        return "Email sent"

    def get_success_url(self):
        return reverse_lazy('service_catalog:emailtemplate_list')

    def get_permission_required(self):
        return 'service_catalog.send_email_template'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        email_template_id = self.kwargs['pk']
        email_template = get_object_or_404(EmailTemplate, pk=email_template_id)
        kwargs.update({
            'email_template': email_template
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['icon_button'] = "fas fa-envelope"
        context['text_button'] = "Send email"
        context['color_button'] = "primary send_email_template"
        return context
