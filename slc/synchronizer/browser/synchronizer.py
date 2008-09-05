import Acquisition, types
from zope.interface import implements
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from interfaces import ISynchronizer


class Synchronizer(BrowserView):
    """ 
    """
    implements(ISynchronizer)
    
    template = ViewPageTemplateFile('synchronizer.pt')

    def __call__(self):

        return self.template() 


    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def setProxy(self, proxy):
        """ used for testing currently..."""
        self.proxy = proxy


    def getSyncStatus(self):
        """ return status about last syndication """
        return self.proxy.getSyncStatus(self.context.UID())


    def syncObject(self, portal_type, data={}, remote_uid=None, translation_reference_uid=None):
        """ check if an object to the given remote_uid exists
            if not, create one using the portal_type
            update its data using the data mapping
            returns a feedback message and the link of the object in question
        """
        return self.proxy.syncObject(portal_type, data, remote_uid, translation_reference_uid)

