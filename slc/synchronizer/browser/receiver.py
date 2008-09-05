import Acquisition, types
from zope.interface import implements
from zope.component import queryUtility
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from slc.synchronizer.interfaces import IReceiver, IUIDMappingStorage

class InvalidCatalogResponseError:
    pass

class Receiver(BrowserView):
    """ 
    """
    implements(IReceiver)
    
    
    def _get_obj_by_remote_uid(self, site_id, remote_uid):

        storage = queryUtility(IUIDMappingStorage)
        local_uid = storage.get(site_id, remote_uid)

        uid_cat = self.context.uid_catalog
        res = uid_cat(UID=local_uid)
        if len(res) == 0:
            return None
        elif len(res)>1:
            raise InvalidCatalogResponseError
        brain = res[0]
        if brain is None:
            raise InvalidCatalogResponseError
        return brain        
    
    def getSyncStatus(self, site_id, remote_uid):
        """ return status about last syndication """

        brain = self._get_obj_by_remote_uid(site_id, remote_uid)
        
        return brain and brain.ModificationDate or brain

    def syncObject(self, portal_type, data={}, site_id='', remote_uid=None, translation_reference_uid=None):
        """ check if an object to the given remote_uid exists
            if not, create one using the portal_type
            update its data using the data mapping
            returns a feedback message and the link of the object in question
        """
        brain = self._get_obj_by_remote_uid(site_id, remote_uid)

        storage = queryUtility(IUIDMappingStorage)
        
        if brain is None:
            # adding new object
            _ = self.context.invokeFactory(id=data['id'], type_name=portal_type)
            ob = getattr(self.context, _)
            ob.processForm(data=1, metadata=1, values=data)
            storage.add(site_id, remote_uid, ob.UID())
            return "Object created successfully", ob.absolute_url()
            
        else:
            # editing existing object
            ob = brain.getObject()
            ob.processForm(data=1, metadata=1, values=data)
            return "Object modified successfully", ob.absolute_url()
                             

