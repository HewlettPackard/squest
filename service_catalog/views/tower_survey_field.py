from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from Squest.utils.squest_views import SquestPermissionDenied
from service_catalog.forms.tower_survey_field_form import TowerSurveyFieldForm
from service_catalog.models import Operation, TowerSurveyField


def operation_edit_survey(request, pk):
    target_operation = get_object_or_404(Operation, id=pk)
    if not request.user.has_perm('service_catalog.change_operation', target_operation):
        raise SquestPermissionDenied('service_catalog.change_operation')
    survey_selector_form_set = modelformset_factory(TowerSurveyField,
                                                    form=TowerSurveyFieldForm,
                                                    extra=0)
    formset = survey_selector_form_set(queryset=target_operation.tower_survey_fields.all())

    if request.method == 'POST':
        formset = survey_selector_form_set(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect(target_operation.service.get_absolute_url())

    breadcrumbs = [
        {'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
        {'text': 'Services', 'url': reverse('service_catalog:service_list')},
        {'text': target_operation.service.name, 'url': target_operation.service.get_absolute_url()},
        {'text': "Operation", 'url': ''},
        {'text': target_operation.name, 'url': ""},
        {'text': "Survey", 'url': ''},
    ]
    context = {'formset': formset,
               'service': target_operation.service,
               'operation': target_operation,
               'breadcrumbs': breadcrumbs}
    return render(request,
                  'service_catalog/admin/service/operation/operation-edit-survey.html', context)
