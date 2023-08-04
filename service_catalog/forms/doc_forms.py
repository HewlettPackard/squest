from martor.fields import MartorFormField
from martor.widgets import AdminMartorWidget

from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models.documentation import Doc


class DocForm(SquestModelForm):
    content = MartorFormField(widget=AdminMartorWidget())

    class Meta:
        model = Doc
        fields = '__all__'
