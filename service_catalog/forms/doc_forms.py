import urllib3
from martor.fields import MartorFormField
from martor.widgets import AdminMartorWidget
from service_catalog.models.documentation import Doc

from Squest.utils.squest_model_form import SquestModelForm

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DocForm(SquestModelForm):
    content = MartorFormField(widget=AdminMartorWidget())

    class Meta:
        model = Doc
        fields = '__all__'
