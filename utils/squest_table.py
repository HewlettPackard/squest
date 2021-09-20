from django_tables2 import tables


class SquestTable(tables.Table):

    def __init__(self, *args, **kwargs):
        hide_field = list()
        if 'hide_fields' in kwargs:
            hide_field = kwargs.pop("hide_fields")
        super(SquestTable, self).__init__(*args, **kwargs)

        for field in hide_field:
            self.columns.hide(field)
