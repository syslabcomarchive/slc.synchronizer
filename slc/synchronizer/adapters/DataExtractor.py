from slc.synchronizer import interfaces
from Products.Archetypes import interfaces as atinterfaces
from zope import interface
from zope import component


class BaseDataExtractor(object):
    """ 
    """
    interface.implements(interfaces.IDataExtractor)
    component.adapts(atinterfaces.IBaseObject)


    def __init__(self, context):
        self.context = context


    def __call__(self):
        data = dict()
        fields = self.context.Schema().fields()
        for field in fields:
            fname = field.getName()
            ftype = field.getType()
            if ftype == 'Products.Archetypes.Field.ReferenceField':
                data[fname] = field.getRaw(self.context)
            else:
                value = field.getAccessor(self.context)()
                data[fname] = value
        return data
