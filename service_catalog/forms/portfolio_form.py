from django.forms import ImageField, FileInput

from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models.portfolio import Portfolio


class PortfolioForm(SquestModelForm):
    class Meta:
        model = Portfolio
        fields = ["name", "description", "image"]

    image = ImageField(
        label="Choose a file",
        required=False,
        widget=FileInput()
    )

    def __init__(self, *args, **kwargs):
        parent_portfolio = kwargs.pop('parent_portfolio')
        super(PortfolioForm, self).__init__(*args, **kwargs)
        self.instance.parent_portfolio = Portfolio.objects.get(id=parent_portfolio) if parent_portfolio else None
