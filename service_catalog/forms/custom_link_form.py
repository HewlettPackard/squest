from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models.custom_link import CustomLink


class CustomLinkForm(SquestModelForm):
    class Meta:
        model = CustomLink
        fields = ["name", "services", "text", "url", "button_class", "when", "loop", "enabled", "is_admin_only"]
