from Squest.utils.squest_model_form import SquestModelForm
from profiles.models import GlobalScope


class GlobalScopeForm(SquestModelForm):
    class Meta:
        model = GlobalScope
        fields = ["global_permissions", "owner_permissions"]
