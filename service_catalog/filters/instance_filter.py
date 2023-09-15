from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import HiddenInput, CheckboxInput
from django.utils.translation import gettext_lazy as _
from django_filters import MultipleChoiceFilter, BooleanFilter, BaseInFilter, CharFilter

from Squest.utils.squest_filter import SquestFilter
from profiles.models import Scope, AbstractScope, GlobalPermission
from service_catalog.models import Instance, Service
from service_catalog.models.instance import InstanceState


def validate_json_field(value):
    if value.count('=') != value.count(',') + 1:
        raise ValidationError(
            _("You must used field accessor by dot (key or index) with its value separated by an equal. Multiple filter"
              " may be separated by commas. See the documentation for examples."),
            params={'value': value},
        )


class CharInFilter(BaseInFilter, CharFilter):
    pass


class InstanceFilter(SquestFilter):
    class Meta:
        model = Instance
        fields = ['name', 'requester', 'service', 'state', 'quota_scope']

    state = MultipleChoiceFilter(choices=InstanceState.choices)
    quota_scope = MultipleChoiceFilter(
        choices=AbstractScope.objects.filter(id__in=Scope.objects.values_list("id",flat=True)).values_list("id", "name"))
    service = MultipleChoiceFilter(choices=Service.objects.values_list("id", "name"))
    requester = MultipleChoiceFilter(choices=User.objects.values_list("id", "username"))
    no_requesters = BooleanFilter(method='no_requester', label="No requester", widget=CheckboxInput())

    spec = CharInFilter(label="Admin spec contains",
                        method='spec_filter',
                        validators=[validate_json_field],
                        help_text="JSON accessor, see the documentation for usage.")
    user_spec = CharInFilter(label="User spec contains",
                             method='user_spec_filter',
                             validators=[validate_json_field],
                             help_text="JSON accessor, see the documentation for usage.")

    def no_requester(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(requester=None)

    def spec_filter(self, queryset, name, value):
        return json_filter(queryset, name, value, 'spec')

    def user_spec_filter(self, queryset, name, value):
        return json_filter(queryset, name, value, 'user_spec')


def json_filter(queryset, name, value, field):
    queries = Q()
    for type in value:
        key = f"{field}__" + type.split('=')[0].replace('.', '__')
        value = type.split('=')[1].replace("\"", "").replace("\'", "")
        queries |= Q(**{key: value})
    if queries:
        queryset = queryset.filter(queries)
    return queryset
