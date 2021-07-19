from django.contrib.auth.models import User
from django.db import models


class BillingGroup(models.Model):
    name = models.CharField(max_length=100,
                            blank=False,
                            unique=True)

    user_set = models.ManyToManyField(
        User,
        blank=True,
        help_text="The users in this billing group.",
        related_name="billing_groups",
        related_query_name="billing_groups",
    )

    def __str__(self):
        return self.name
