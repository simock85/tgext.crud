from tg import expose, validate, redirect, request, url
from validators import EntityValidator
from sprox.tablebase import TableBase
from tw.forms.datagrid import Column
from webhelpers.html.tags import link_to
import new

def create_setter(crud_controller, err_handler, config):
    provider = crud_controller.provider
    model = crud_controller.model

    @expose()
    @validate({'obj':EntityValidator(provider, model)}, error_handler=err_handler)
    def autogenerated_setter(self, obj):
        name, value = config
        setattr(obj, name, callable(value) and value(obj) or value)
        return redirect('../')

    return new.instancemethod(autogenerated_setter, crud_controller, crud_controller.__class__)

def set_table_filler_getter(filler, name, function):
    meth = new.instancemethod(function, filler, filler.__class__)
    setattr(filler, name, meth)

class SortableColumn(Column):
    def __init__(self, name, *args, **kw):
        super(SortableColumn, self).__init__(name, *args, **kw)
        self._title_ = kw.get('title', name.capitalize())

    def set_title(self, title):
        self._title_ = title

    def get_title(self):
        current_ordering = request.GET.get('order_by')
        if current_ordering == self.options['sort_field'] and not request.GET.get('desc'):
            desc = 1
        else:
            desc = 0

        new_params = dict(request.GET)
        if desc:
            new_params['desc'] = 1
        else:
            new_params.pop('desc', None)
        new_params['order_by'] = self.options['sort_field']

        return link_to(self._title_, url=url(request.path_url, params=new_params))

    title = property(get_title, set_title)

class SortableTableBase(TableBase):
    def _do_get_widget_args(self):
        args = super(SortableTableBase, self)._do_get_widget_args()

        adapted_fields = []
        entity_fields = self.__provider__.get_fields(self.__entity__)
        for field in args['fields']:
            if field[0] in entity_fields and not self.__provider__.is_relation(self.__entity__, field[0]):
                field = SortableColumn(field[0],
                                       getter=field[1],
                                       title=field[0],
                                       options={'sort_field':field[0]})
            adapted_fields.append(field)

        args['fields'] = adapted_fields
        return args
