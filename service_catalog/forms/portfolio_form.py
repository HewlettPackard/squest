from django.forms import ImageField, FileInput

from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models.portfolio import Portfolio


class PortfolioForm(SquestModelForm):
    class Meta:
        model = Portfolio
        fields = ["name", "description", "image", "description_doc", "parent_portfolio"]

    image = ImageField(
        label="Choose a file",
        required=False,
        widget=FileInput()
    )
