from django.contrib.auth.models import Permission
from django.db.models import ForeignKey, CharField, SET_NULL, CASCADE, IntegerField, ManyToManyField

from Squest.utils.squest_model import SquestModel


class ApprovalStep(SquestModel):
    class Meta:
        unique_together = (('id', 'approval_workflow'), ('name', 'approval_workflow'))
        permissions = [('can_approve_approvalstep', 'Can approve an approval step')]

    approval_workflow = ForeignKey(
        "service_catalog.ApprovalWorkflow",
        blank=False,
        null=False,
        on_delete=CASCADE,
        related_name="approval_steps"
    )

    name = CharField(max_length=100, blank=False)
    position = IntegerField(null=True, blank=True, default=0)

    next = ForeignKey(
        "service_catalog.ApprovalStep",
        blank=True,
        null=True,
        default=None,
        on_delete=SET_NULL,
        related_name="previous"
    )

    permission = ForeignKey(
        Permission,
        blank=True,
        null=True,
        default=None,
        on_delete=SET_NULL,
        related_name="previous"
    )

    readable_fields = ManyToManyField(
        'service_catalog.TowerSurveyField',
        blank=True,
        help_text="Read only field",
        related_name="approval_steps_as_read_field"
    )

    editable_fields = ManyToManyField(
        'service_catalog.TowerSurveyField',
        blank=True,
        help_text="Fields allowed to be filled",
        related_name="approval_steps_as_write_field"
    )

    def __str__(self):
        return self.name
