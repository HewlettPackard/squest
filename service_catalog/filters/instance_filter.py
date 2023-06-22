from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.forms import HiddenInput, CheckboxInput
from django_filters import MultipleChoiceFilter, BooleanFilter, BaseInFilter, CharFilter

from service_catalog.models import Instance, Service
from service_catalog.models.instance import InstanceState
from Squest.utils.squest_filter import SquestFilter


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
        fields = ['name', 'id', 'requester', 'service', 'state']

    requester = MultipleChoiceFilter()
    state = MultipleChoiceFilter(choices=InstanceState.choices)
    service = MultipleChoiceFilter()

    no_requesters = BooleanFilter(method='no_requester', label="No requester", widget=CheckboxInput())

    spec = CharInFilter(label="Admin spec contains",
                        method='spec_filter',
                        validators=[validate_json_field],
                        help_text="JSON accessor, see the documentation for usage.")
    user_spec = CharInFilter(label="User spec contains",
                             method='user_spec_filter',
                             validators=[validate_json_field],
                             help_text="JSON accessor, see the documentation for usage.")

    def __init__(self, *args, **kwargs):
        super(InstanceFilter, self).__init__(*args, **kwargs)
        self.filters['id'].field.widget = HiddenInput()
        self.filters['service'].field.choices = [(service.id, service.name) for service in Service.objects.all().order_by("name")]
        self.filters['requester'].field.choices = [(requester.id, requester.username) for requester in User.objects.all().order_by("username")]

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
