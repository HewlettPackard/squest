from django.urls import reverse

from profiles.models.squest_permission import Permission
from django.db.models import ForeignKey, CharField, SET_NULL, CASCADE, IntegerField, ManyToManyField, PROTECT, Q
from django.db.models.signals import post_save

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
        on_delete=PROTECT,
        related_name="previous",
        limit_choices_to={"content_type__app_label": "service_catalog", "content_type__model": "approvalstep"}
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

    @classmethod
    def on_create_set_position(cls, sender, instance, created, *args, **kwargs):
        if created:
            if instance.position == 0:
                previous_steps = ApprovalStep.objects.filter(
                    approval_workflow=instance.approval_workflow).order_by('position').exclude(id=instance.id)
                if previous_steps.exists():
                    instance.position = previous_steps.last().position + 1
                    instance.save()

    def save(self, *args, **kwargs):
        # set the default permission
        if not hasattr(self, "permission"):
            self.permission = Permission.objects.get(codename="can_approve_approvalstep")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("service_catalog:approvalworkflow_details", args=[self.pk])

    def get_scopes(self):
        return self.approval_workflow.get_scopes()

    def who_can_approve(self, scope):
        return scope.who_has_perm(self.permission.permission_str)


post_save.connect(ApprovalStep.on_create_set_position, sender=ApprovalStep)
