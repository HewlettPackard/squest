from django_tables2 import tables, TemplateColumn

from profiles.models import InstanceNotification, RequestNotification


class RequestNotificationFilterTable(tables.Table):
    actions = TemplateColumn(template_name='generics/custom_columns/generic_actions.html', orderable=False)

    class Meta:
        model = RequestNotification
        attrs = {"id": "request_notification_filter__table", "class": "table squest-pagination-tables "}
        fields = ("name", "actions")


class InstanceNotificationFilterTable(tables.Table):
    actions = TemplateColumn(template_name='generics/custom_columns/generic_actions.html', orderable=False)

    class Meta:
        model = InstanceNotification
        attrs = {"id": "support_notification_filter__table", "class": "table squest-pagination-tables "}
        fields = ("name", "actions")
