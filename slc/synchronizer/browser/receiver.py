import Acquisition, types
from zope.interface import implements
from zope.component import queryUtility
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from slc.synchronizer.interfaces import IReceiver, IUIDMappingStorage, IObjectFinder
from types import *
import logging

logger = logging.getLogger('slc.synchronizer.receiver')
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
        #Temporary sort of hack
        self.REQUEST = self.request
        res = uid_cat(UID=local_uid)
        if len(res) == 0:
            return None
        elif len(res) > 1:
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

    def _add_translation(self, ob, site_id, translation_reference_uid):
        canonical = self._get_obj_by_remote_uid(site_id, translation_reference_uid)
        if canonical is None:
            return
        canonical = canonical.getObject()
        if not ob.hasTranslation(canonical.Language()):
            ob.addTranslationReference(canonical)
            canonical.invalidateTranslationCache()


    def syncObject(self, portal_type,
                         data={},
                         site_id='',
                         remote_uid=None,
                         translation_reference_uid=None):
        """ check if an object to the given remote_uid exists
            if not, create one using the portal_type
            update its data using the data mapping
            returns a feedback message and the link of the object in question
        """
        storage = queryUtility(IUIDMappingStorage)

        newdata = data.copy()
        for i in data.keys():
            value = data[i]
            if value == "[[None]]":
                del newdata[i]
                ##newdata[i] = None
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
                if type(value) == TupleType:
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
            # The object finder wil not be invoked when dealing with a translation.
            if not translation_reference_uid:
                finder = queryUtility(IObjectFinder)
                ob = finder(data, portal_type)
            else:
                ob = None
            # nothing found, add a new object
            if ob is None:
                try:
                    _ = self.context.invokeFactory(id=data['id'], type_name=portal_type)
                except ValueError, ve:
                    import traceback; traceback.print_exc()
                    logger.error(str(ve))
                    return 1, str(ve), ''
                except Exception, e:
                    import traceback; traceback.print_exc()
                    logger.error(str(e))
                    return 2, str(e), ''
                ob = getattr(self.context, _)
                # we send an id, we want it to stay this way!
                ob._at_rename_after_creation = False
                msg = "Object created successfully"
            else:
                # object exists, don't change its id
                if newdata.has_key('id'):
                    del newdata['id']
                msg = "Existing object edited successfully"
            ob.processForm(data=1, metadata=1, values=newdata)
            self._add_translation(ob, site_id, translation_reference_uid)
            storage.add(site_id, remote_uid, ob.UID())
            return 0, msg, ob.absolute_url()
        else:
            # editing existing, previously synchronized object
            ob = brain.getObject()
            # object exists, don't change its id
            if newdata.has_key('id'):
                del newdata['id']

            ob.processForm(data=1, metadata=1, values=newdata)
            self._add_translation(ob, site_id, translation_reference_uid)
            storage.add(site_id, remote_uid, ob.UID())
            return 0, "Object modified successfully", ob.absolute_url()


