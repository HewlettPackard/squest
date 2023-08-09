from django.db import models
from django.db.models import ForeignKey, Sum, Q
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse

from Squest.utils.squest_model import SquestModel


class Quota(SquestModel):
    class Meta:
        unique_together = ('scope', 'attribute_definition')
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    scope = ForeignKey("Scope",
                       blank=False,
                       help_text="The attribute definitions linked to this quota.",
                       related_name="quotas",
                       related_query_name="quota",
                       verbose_name="Scope",
                       on_delete=models.CASCADE
                       )
    limit = models.PositiveIntegerField(default=0)
    attribute_definition = ForeignKey(
        "resource_tracker_v2.AttributeDefinition",
        blank=False,
        help_text="The attribute definitions linked to this quota.",
        related_name="quotas",
        related_query_name="quota",
        verbose_name="Attribute",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.attribute_definition.name

    def get_scopes(self):
        return self.scope.get_scopes()

    @property
    def name(self):
        return self.attribute_definition.name

    @property
    def available(self):
        return self.limit - self.consumed

    @property
    def consumed(self):
        from resource_tracker_v2.models import ResourceAttribute
        # get the consumption of instances at scope level (org or team)
        consumed = ResourceAttribute.objects.filter(attribute_definition=self.attribute_definition,
                                                    resource__service_catalog_instance__quota_scope=self.scope) \
            .values("resource__service_catalog_instance__quota_scope") \
            .aggregate(consumed=Sum('value')) \
            .get("consumed", 0)
        if consumed is None:  # the previous call has returned None if there is no instance linked to the org
            consumed = 0

        # if the scope is an org, we subtract the limit of each team to the global consumption
        class_name = self.scope.get_object().__class__.__name__
        if class_name == "Organization":
            target_org = self.scope.get_object()
            team_consumed = Quota.objects.filter(scope__in=target_org.teams.all(),
                                                 attribute_definition=self.attribute_definition) \
                .aggregate(limit=Sum('limit')) \
                .get("limit", 0)
            if team_consumed is not None:
                consumed = consumed + team_consumed

        return consumed

    @classmethod
    def get_q_filter(cls, user, perm):
        from profiles.models import Team
        app_label, codename = perm.split(".")
        return Q(
            scope__rbac__user=user,
            scope__rbac__role__permissions__codename=codename,
            scope__rbac__role__permissions__content_type__app_label=app_label
        ) | Q(
            ### Scopes - Org - Default roles
            scope__rbac__user=user,
            scope__roles__permissions__codename=codename,
            scope__roles__permissions__content_type__app_label=app_label
        ) | Q(
            ## Scopes - Team - User
            scope__in=Team.objects.filter(
                org__rbac__user=user,
                org__rbac__role__permissions__codename=codename,
                org__rbac__role__permissions__content_type__app_label=app_label
            )
        ) | Q(
            ## Scopes - Team - Default roles
            scope__in=Team.objects.filter(
                org__rbac__user=user,
                org__roles__permissions__codename=codename,
                org__roles__permissions__content_type__app_label=app_label
            )
        )


@receiver(post_delete, sender=Quota)
def on_delete(sender, instance: Quota, **kwargs):
    # Delete all team quotas when org quota is deleted
    if instance.scope.is_org:
        instance.scope.get_object().teams
        Quota.objects.filter(scope__id__in=instance.scope.get_object().teams.values_list('id', flat=True),
                             attribute_definition=instance.attribute_definition).delete()
