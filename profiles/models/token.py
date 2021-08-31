import binascii
import os

from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone


class Token(models.Model):
    """
    An API token used for user authentication. This extends the stock model to allow each user to have multiple tokens.
    It also supports setting an expiration time and toggling write ability.
    """

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='tokens'
    )
    created = models.DateTimeField(
        blank=True,
        null=True
    )
    expires = models.DateTimeField(
        blank=True,
        null=True
    )
    key = models.CharField(
        max_length=40,
        unique=True,
        validators=[MinLengthValidator(40)]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.created:
            self.created = timezone.now()
        if not self.expires:
            self.expires = self.created + timezone.timedelta(days=1)
        if not self.key:
            self.key = self.generate_key()

    def __str__(self):
        # Only display the last 24 bits of the token to avoid accidental exposure.
        return "{} ({})".format(self.key[-6:], self.user)

    def generate_key(self):
        # Generate a random 160-bit key expressed in hexadecimal.
        return binascii.hexlify(os.urandom(20)).decode()

    def update_key(self):
        self.key = self.generate_key()
        self.expires = timezone.now() + timezone.timedelta(days=1)
        self.save()

    def set_expiration_date(self, date):
        self.expires = date
        self.save()

    def is_expired(self):
        if self.expires is None or timezone.now() < self.expires:
            return False
        return True
