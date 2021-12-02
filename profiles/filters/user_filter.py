from django.contrib.auth.models import User
from Squest.utils.squest_filter import SquestFilter


class UserFilter(SquestFilter):
    class Meta:
        model = User
        fields = ['username', 'email']
