import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.template import Context
from django.template.loader import get_template
from django.urls import reverse
from django.utils.safestring import mark_safe
from graphviz import Digraph
from taggit.models import Tag

from resource_tracker_v2.filters.resource_group_filter import ResourceGroupFilter
from resource_tracker_v2.filters.tag_filter import TagFilterset
from resource_tracker_v2.models import ResourceGroup
from resource_tracker_v2.views.utils.tag_session_manager import tag_session_manager

logger = logging.getLogger(__name__)

COLORS = {'consumer': '#28a745', 'provider': '#dc3545', 'resource_pool': '#ff851b', 'resource_group': '#17a2b8',
          'available': '#ffc107', "green": "#28a745", "yellow": "#ffc107", "red": "#dc3545",
          'transparent': '#ffffff00', 'gray': '#6c757d', 'light': '#f8f9fa'}


@login_required
def resource_tracker_graph(request):
    if not request.user.has_perm('resource_tracker_v2.list_resourcegroup'):
        raise PermissionDenied
    redirect_url = tag_session_manager(request)
    if redirect_url:
        return redirect_url

    dot = Digraph(comment='Graph')
    dot.attr(bgcolor=COLORS["transparent"])
    dot.name = 'Resource Tracker Graph'
    dot.attr('node', shape='plaintext')

    tags = Tag.objects.all()
    resource_graph_filtered = TagFilterset(request.GET, queryset=tags)
    display_graph = False

    resource_group_filter = ResourceGroupFilter(request.GET, queryset=ResourceGroup.objects.all())
    resource_group_filter.is_valid()
    resource_group_queryset = resource_group_filter.qs

    for resource_group in resource_group_queryset:
        display_graph = True
        dot.node(f'{resource_group}', label=create_resource_group_svg(resource_group))
        for transformer in resource_group.transformers.all():
            rg = f'{resource_group}:{transformer.attribute_definition.name}'
            if transformer.consume_from_resource_group:
                target = f'{transformer.consume_from_resource_group.name}:{transformer.consume_from_attribute_definition.name}'
                dot.edge(target, rg, color=COLORS['consumer'])

    dot.format = 'svg'
    svg = mark_safe(dot.pipe().decode('utf-8'))

    return render(
        request,
        'resource_tracker_v2/graph/resource-tracker-graph.html',
        context={
            'svg': svg,
            'display_graph': display_graph,
            'resource_graph': resource_graph_filtered,
            'resource_groups': resource_group_queryset
        }
    )


def create_resource_group_svg(resource_group: ResourceGroup):
    context = dict()
    context['name'] = {
        'display': resource_group.name,
        'tooltip': f"Go to {resource_group}",
        'href': reverse('resource_tracker_v2:resourcegroup_edit',
                        kwargs={'pk': resource_group.id})}
    context['count'] = {
                           'display': resource_group.resources.count(),
                           'tooltip': f"Go to {resource_group}'s resources",
                           'href': reverse('resource_tracker_v2:resource_list',
                                           kwargs={'resource_group_id': resource_group.id}),
                           'color': COLORS["light"]
                       }
    context['transformers'] = [
        {
            'name': {
                'display': transformer.attribute_definition.name,
                'tooltip': f"Edit transformer {transformer.attribute_definition.name}",
                'href': reverse('resource_tracker_v2:transformer_edit',
                                kwargs={'resource_group_id': resource_group.id,
                                        'attribute_id': transformer.attribute_definition.id})},
            'produced': {
                'display': round(transformer.total_produced),
                'tooltip': f"Sum of resource on this attribute",
                'color': COLORS["light"]
            },
            'consumed': {
                'display': f"{round(transformer.total_consumed)}",
                'tooltip': f"Sum of resource on this attribute from other resource group",
                'color': COLORS["light"]
            },
            'available': {
                'display': f"{round(transformer.available)}",
                'color': COLORS["light"]
            },
            'percent': {
                'display': f"{transformer.percent_consumed}",
                'color': COLORS[transformer.progress_bar_color],
                'tooltip': f"Percentage of consumption",
                'text_color': transformer.progress_bar_text_color
            }
        }
        for transformer in resource_group.transformers.all()
    ]
    context['color'] = COLORS['resource_group']
    context['resource_group'] = resource_group

    tm = get_template('resource_tracker_v2/graph/resource_group.html').template
    return tm.render(context=Context(context))
