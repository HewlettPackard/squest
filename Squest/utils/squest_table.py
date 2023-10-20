from django_tables2 import tables, RequestConfig


class SquestTable(tables.Table):

    def __init__(self, *args, **kwargs):
        hide_field = list()
        if 'hide_fields' in kwargs:
            hide_field = kwargs.pop("hide_fields")
        super(SquestTable, self).__init__(*args, **kwargs)

        for field in hide_field:
            if field in self.columns.columns:
                self.columns.hide(field)

class SquestRequestConfig(RequestConfig):

    def __init__(self, request, paginate=False):
        self.request = request
        self.paginate = paginate
