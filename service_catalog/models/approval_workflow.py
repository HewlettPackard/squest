from django.core.exceptions import ValidationError
from django.db.models import CharField, Model, SET_NULL, ForeignKey
from django.utils.translation import gettext_lazy as _


class ApprovalWorkflow(Model):
    name = CharField(max_length=100, blank=False, unique=True)
    entry_point = ForeignKey(
        "service_catalog.ApprovalStep",
        blank=True,
        null=True,
        default=None,
        on_delete=SET_NULL,
        related_name="approval_workflow_entry"
    )

    def __str__(self):
        return self.name

    def clean(self):
        if self.entry_point and self.entry_point.approval_workflow != self:
            raise ValidationError({'entry_point': _("The entry point must be in the workflow.")})

    def update_positions(self):
        """
        update positions of all approval step in the approval workflow
        """
        current = self.entry_point
        position = 1
        approval_step_to_update = list()
        while current is not None:
            current.refresh_from_db()
            approval_step_to_update.append(current)
            approval_step_to_update[-1].position = position
            position += 1
            current = current.next
        from service_catalog.models import ApprovalStep
        # bulk update is used to skip signals
        ApprovalStep.objects.bulk_update(approval_step_to_update, ['position'])
