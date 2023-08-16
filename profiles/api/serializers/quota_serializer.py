from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from profiles.models import Quota


class QuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quota
        fields = ['id', 'scope', 'attribute_definition', 'limit']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        scope = self.instance.scope if self.instance else None
        scope = attrs['scope'] if 'scope' in attrs.keys() else scope
        attribute_definition = attrs.get("attribute_definition")
        limit = attrs.get("limit")

        current_quota = Quota.objects.filter(scope=scope, attribute_definition=attribute_definition).first()
        current_limit = 0
        current_consumed = 0

        if current_quota:
            current_limit = current_quota.limit
            current_consumed = current_quota.consumed

        if scope.is_org:
            consumed = current_consumed
            if limit < consumed:
                msg = f"Limit can not be less than the consumption at Team level. Already consumed: {consumed} {attribute_definition}"
                error = {'limit': msg}
                raise ValidationError(error)

        elif scope.is_team:
            try:
                parent_organization = scope.get_object().org
                parent_quota = Quota.objects.get(scope_id=parent_organization.id,
                                                 attribute_definition=attribute_definition)
            except Quota.DoesNotExist:
                msg = f"Quota need to be set at org level first."
                error = {'limit': msg}
                raise ValidationError(error)

            max_value = parent_quota.available + current_limit
            available = max_value
            if limit > available:
                msg = f"Limit can not be more than the limit at the Organization level. Organization limit: {max_value} {attribute_definition}"
                error = {'limit': msg}
                raise ValidationError(error)
        return attrs
