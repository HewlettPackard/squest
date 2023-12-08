from django.urls import reverse
from django.utils.html import format_html
from django_tables2 import TemplateColumn, LinkColumn, CheckBoxColumn, Column

from Squest.utils.squest_table import SquestTable
from service_catalog.models import Request


class RequestTable(SquestTable):
    selection = CheckBoxColumn(accessor='pk', attrs={"th__input": {"onclick": "toggle(this)"}})
    id = Column(linkify=True, verbose_name="Request")
    date_submitted = TemplateColumn(template_name='generics/custom_columns/generic_date_format.html')
    instance = LinkColumn()
    last_updated = TemplateColumn(template_name='generics/custom_columns/generic_date_format.html')
    instance__quota_scope__name = Column(verbose_name="Quota scope")

    def before_render(self, request):
        if not request.user.has_perm('service_catalog.delete_request'):
            self.columns.hide('selection')

    class Meta:
        model = Request
        attrs = {"id": "request_table", "class": "table squest-pagination-tables"}
        fields = ("selection", "id", "user__username", "instance__quota_scope__name",
                  "instance__service", "operation", "state", "instance", "date_submitted",
                  "last_updated")

    def render_operation(self, value, record):
        from service_catalog.views import map_operation_type
        return format_html(
            f'<strong class="text-{map_operation_type(record.operation.type)}">{value.name}</strong>')

    def render_id(self, value, record):
        return format_html(f'<a title={value} href="{record.get_absolute_url()}">{record}</a>')

    def render_state(self, record, value):
        from service_catalog.views import map_request_state
        if record.approval_workflow_state is not None and record.approval_workflow_state.current_step is not None:
            position = record.approval_workflow_state.current_step.approval_step.position
            number_of_steps = record.approval_workflow_state.approval_step_states.count()
            return format_html(
                f'<a href="{record.get_absolute_url()}"><strong class="text-{map_request_state(record.state)}">{value} ({position}/{number_of_steps})</strong></a>')

        return format_html(
            f'<a href="{record.get_absolute_url()}"><strong class="text-{map_request_state(record.state)}">{value}</strong></a>')


class RequestTablesForApprovalWorkflow(RequestTable):
    approval_workflow_state__hash = Column(verbose_name="Approval workflow hash")
    approval_workflow_state__approval_workflow__name = Column(verbose_name="Approval workflow name")

    class Meta(RequestTable.Meta):
        fields = (
            "id", "approval_workflow_state__approval_workflow__name", "approval_workflow_state__hash", "user__username",
            "instance__quota_scope__name", "instance__service", "operation", "state", "instance")

    def render_approval_workflow_state__hash(self, value, record):
        return hex(value)


class RequestTableWaitingForActions(SquestTable):
    id = Column(linkify=True, verbose_name="Request", orderable=False)
    user__username = Column(orderable=False)
    instance = LinkColumn(orderable=False)
    instance__quota_scope__name = Column(verbose_name="Quota scope", orderable=False)
    review = Column(empty_values=(), orderable=False)
    operation = Column(orderable=False)
    state = Column(orderable=False)

    class Meta:
        model = Request
        attrs = {"id": "request_table", "class": "table squest-pagination-tables"}
        fields = ("id", "user__username", "instance__quota_scope__name", "operation", "state", "instance", "review")

    def render_id(self, value, record):
        return format_html(f'<a title={value} href="{record.get_absolute_url()}">{record}</a>')

    def render_operation(self, value, record):
        from service_catalog.views import map_operation_type
        return format_html(f'<strong class="text-{map_operation_type(record.operation.type)}">{value}</strong>')

    def render_state(self, record, value):
        from service_catalog.views import map_request_state
        if record.approval_workflow_state is not None and record.approval_workflow_state.current_step is not None:
            position = record.approval_workflow_state.current_step.approval_step.position
            number_of_steps = record.approval_workflow_state.approval_step_states.count()
            return format_html(
                f'<a href="{record.get_absolute_url()}"><strong class="text-{map_request_state(record.state)}">{value} ({position}/{number_of_steps})</strong></a>')

        return format_html(
            f'<a href="{record.get_absolute_url()}"><strong class="text-{map_request_state(record.state)}">{value}</strong></a>')

    def render_review(self, value, record):
        if record.approval_workflow_state:
            url = reverse("service_catalog:request_approve", kwargs={"pk": record.id})
        else:
            url = reverse("service_catalog:request_accept", kwargs={"pk": record.id})
        return format_html(
            f'<a href="{url}" class="btn btn-primary"> <i class="fas fa-clipboard-check"></i></a>')
