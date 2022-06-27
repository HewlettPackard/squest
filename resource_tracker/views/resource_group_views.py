import logging

from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django_celery_results.models import TaskResult
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from guardian.mixins import LoginRequiredMixin

from resource_tracker.filters.resource_group_filter import ResourceGroupFilter
from resource_tracker.forms import ResourceGroupForm
from resource_tracker.models import ResourceGroup
from resource_tracker.tables.resource_group_attribute_definition_table import ResourceGroupAttributeDefinitionTable
from resource_tracker.tables.resource_group_table import ResourceGroupTable
from resource_tracker.tables.resource_group_text_attribute_definition_table import \
    ResourceGroupTextAttributeDefinitionTable
from service_catalog.tasks import async_recalculate_total_resources

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class ResourceGroupListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = ResourceGroupTable
    model = ResourceGroup
    template_name = 'generics/list.html'
    filterset_class = ResourceGroupFilter

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied

        tag_session_key = f'{self.request.path}__tags'
        filter_button_used = "tag_redirect" in self.request.GET
        tags_from_session = self.request.session.get(tag_session_key, [])
        if len(tags_from_session) > 0 and not filter_button_used:
            logger.info(f"Using tags loaded from session: {tags_from_session}")
            string_tag = "?"
            for tag in tags_from_session:
                string_tag += f"tag={tag}&"
            string_tag += "tag_redirect="  # in order to stop the redirect
            return redirect(reverse("resource_tracker:resource_group_list") + string_tag)
        return super(ResourceGroupListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Resource groups"
        context['app_name'] = "resource_tracker"
        context['object_name'] = "resource_group"
        context['html_button_path'] = "generics/buttons/generic_add_button.html"
        return context

    def get_queryset(self):
        filter_button_used = "tag_redirect" in self.request.GET
        tag_session_key = f'{self.request.path}__tags'
        if "tag" in self.request.GET and not filter_button_used:
            tag_list = self.request.GET.getlist("tag")
            resource_group_list_queryset = ResourceGroup.objects.filter(tags__name__in=tag_list)
            logger.info(f"Settings tags from URL in session: {tag_list}")
            self.request.session[tag_session_key] = tag_list
        else:
            resource_group_list_queryset = ResourceGroup.objects.all()
            self.request.session[tag_session_key] = []
        return resource_group_list_queryset


@user_passes_test(lambda u: u.is_superuser)
def resource_group_edit(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    form = ResourceGroupForm(request.POST or None, instance=resource_group)
    if form.is_valid():
        form.save()
        return redirect("resource_tracker:resource_group_list")
    attribute_table = ResourceGroupAttributeDefinitionTable(resource_group.attribute_definitions.all())
    text_attribute_table = ResourceGroupTextAttributeDefinitionTable(resource_group.text_attribute_definitions.all())
    breadcrumbs = [
        {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': resource_group.name, 'url': ""},
    ]
    context = {'form': form, 'resource_group': resource_group, 'attribute_table': attribute_table,
               'text_attribute_table': text_attribute_table, 'breadcrumbs': breadcrumbs, 'action': 'edit'}
    return render(request,
                  'resource_tracking/resource_group/resource-group-edit.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_create(request):
    if request.method == 'POST':
        form = ResourceGroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("resource_tracker:resource_group_list")
    else:
        form = ResourceGroupForm()
    breadcrumbs = [
        {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': 'Create a new resource group', 'url': ""},
    ]
    context = {'form': form, 'breadcrumbs': breadcrumbs, 'action': 'create'}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_delete(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    if request.method == 'POST':
        # delete all resource attributes
        resource_group.resources.all().delete()
        resource_group.attribute_definitions.all().delete()
        resource_group.text_attribute_definitions.all().delete()
        resource_group.delete()
        # delete all resources
        return redirect("resource_tracker:resource_group_list")
    breadcrumbs = [
        {'text': 'Resource groups', 'url': reverse('resource_tracker:resource_group_list')},
        {'text': resource_group.name, 'url': ""},
    ]
    context = {'resource_group': resource_group, 'breadcrumbs': breadcrumbs}
    return render(request,
                  'resource_tracking/resource_group/resource-group-delete.html', context)


@user_passes_test(lambda u: u.is_superuser)
def resource_group_recalculate_total_resources(request, resource_group_id):
    task = async_recalculate_total_resources.delay(resource_group_id)
    task_result = TaskResult(task_id=task.task_id)
    task_result.save()
    request.session['task_id'] = task_result.id
    if 'HTTP_REFERER' in request.META:
        return redirect(request.META['HTTP_REFERER'])
    return redirect(reverse('resource_tracker:resource_group_list'))
