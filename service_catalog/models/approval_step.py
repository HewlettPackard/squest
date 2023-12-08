from django.db.models import ForeignKey, CharField, SET_NULL, CASCADE, IntegerField, ManyToManyField, PROTECT, TextField
from django.db.models.signals import post_save
from django.urls import reverse
from hashlib import sha256

from Squest.utils.squest_model import SquestModel
from profiles.models.squest_permission import Permission


class ApprovalStep(SquestModel):
    class Meta(SquestModel.Meta):
        unique_together = (('id', 'approval_workflow'), ('name', 'approval_workflow'))
        permissions = [('approve_reject_approvalstep', 'Can approve/reject  an approval step')]

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
        related_name="approval_step",
        limit_choices_to={"content_type__app_label": "service_catalog",
                          "content_type__model": "approvalstep"}
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

    auto_accept_condition = TextField(blank=True, null=True,
                                      help_text="Ansible like 'when' with `request` as context. "
                                                "No Jinja brackets needed",
                                      default=None)

    def __str__(self):
        return self.name

    @property
    def hash(self):
        string = ""
        string += f"{self.id}_"
        string += f"{self.position}_"
        string += f"{self.permission.id}_"
        string += f"{list(self.readable_fields.values_list('id', flat=True))}_"
        string += f"{list(self.editable_fields.values_list('id', flat=True))}_"
        string += f"{self.auto_accept_condition}_"
        return int(sha256(string.encode("utf-8")).hexdigest(), 16) % 2 ** 31

    @classmethod
    def on_create_set_position(cls, sender, instance, created, *args, **kwargs):
        if created:
            if instance.position == 0:
                previous_steps = ApprovalStep.objects.filter(
                    approval_workflow=instance.approval_workflow).order_by('position').exclude(id=instance.id)
                if previous_steps.exists():
                    ApprovalStep.objects.filter(id=instance.id).update(position=previous_steps.last().position + 1)

    def save(self, *args, **kwargs):
        # set the default permission
        if not hasattr(self, "permission"):
            self.permission = Permission.objects.get(codename="approve_reject_approvalstep")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("service_catalog:approvalworkflow_details", args=[self.pk])

    def get_scopes(self):
        return self.approval_workflow.get_scopes()

    def who_can_approve(self, scope):
        return scope.who_has_perm(self.permission.permission_str)


post_save.connect(ApprovalStep.on_create_set_position, sender=ApprovalStep)
