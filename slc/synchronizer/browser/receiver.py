import Acquisition, types
from zope.interface import implements
from zope.component import queryUtility
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from slc.synchronizer.interfaces import IReceiver, IUIDMappingStorage, IObjectFinder
from types import *

UNWANTED_ATTRS = ['creation_date', 'modification_date']

class InvalidCatalogResponseError:
    pass



class Receiver(BrowserView):
    """ 
    """
    implements(IReceiver)

    def _get_obj_by_remote_uid(self, site_id, remote_uid):

        storage = queryUtility(IUIDMappingStorage)
        local_uid = storage.get(site_id, remote_uid)

        uid_cat = self.context.portal_catalog
        res = uid_cat(UID=local_uid)
        if len(res) == 0:
            return None
        elif len(res)>1:
            raise InvalidCatalogResponseError
        brain = res[0]
        if brain is None:
            raise InvalidCatalogResponseError
        return brain        
    
    def getSyncStatus(self, site_id='', remote_uid=''):
        """ return status about last syndication """
        try:
            brain = self._get_obj_by_remote_uid(site_id, remote_uid)
        except InvalidCatalogResponseError:
            return (-1, -1)
        if brain is None:
            return (-1, -1)
        return (brain.ModificationDate, brain.getURL())

    def syncObject(self, portal_type, data={}, site_id='', remote_uid=None, translation_reference_uid=None):
        """ check if an object to the given remote_uid exists
            if not, create one using the portal_type
            update its data using the data mapping
            returns a feedback message and the link of the object in question
        """
        storage = queryUtility(IUIDMappingStorage)

        newdata = data.copy()
        for i in data.keys():
            value = data[i]
            if value=="[[None]]":
                newdata[i] = None
            if i in UNWANTED_ATTRS:
                del newdata[i]
            # rewrite the referenced object UIDs using our local uid storage
            if type(value) in [ListType, TupleType]:
                newvals = []
                for val in value:                    
                    if storage.has_remote_uid(site_id, val):
                        newvals.append(storage.get(site_id, val))
                    else:
                        newvals.append(val)
                if type(value)==TupleType:
                    newvals = tuple(newvals)
                newdata[i] = newvals
            else:            
                if storage.has_remote_uid(site_id, value):
                    newdata[i] = storage.get(site_id, value)
            
        brain = self._get_obj_by_remote_uid(site_id, remote_uid)
        
        if brain is None:
            # There is no matching object in our registry. If you want to try to match 
            # an existing object based on whatever criteria to avoid dublettes, you can 
            # use the following hook by providing your own utility to find an object to use
            finder = queryUtility(IObjectFinder)
            ob = finder(data)

            # nothing found, add a new object
            if ob is None:
                try:
                    _ = self.context.invokeFactory(id=data['id'], type_name=portal_type)
                except ValueError, ve:
                    return 1, str(ve), ''
                ob = getattr(self.context, _)
                
            ob.processForm(data=1, metadata=1, values=newdata)
            storage.add(site_id, remote_uid, ob.UID())
            return 0, "Object created successfully", ob.absolute_url()
        else:
            # editing existing object
            ob = brain.getObject()
            ob.processForm(data=1, metadata=1, values=newdata)
            storage.add(site_id, remote_uid, ob.UID())
            return 0, "Object modified successfully", ob.absolute_url()
                             

