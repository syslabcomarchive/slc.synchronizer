import Acquisition, types
from zope.interface import implements
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from slc.synchronizer.interfaces import ISynchronizer
from xmlrpclib import ServerProxy

#XXX: Should also work without Linguaplone
try:
    from Products.LinguaPlone.interfaces import ITranslatable
    HAVE_LP = True
except:
    HAVE_LP = False    
    
class Synchronizer(BrowserView):
    """ 
    """
    implements(ISynchronizer)
    
    template = ViewPageTemplateFile('synchronizer.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.proxy = None


    def __call__(self):
        if self.context.REQUEST.has_key('form.button.Synchronize'):
            self.syncObject(self.context.portal_type, 
                            self.get_data(), 
                            remote_uid=self.context.UID(), 
                            translation_reference_uid=self.get_trans())
        return self.template() 


    def get_trans(self):        
        if not HAVE_LP or not ITranslatable.implementedBy(self.context):
            return ''
        can = self.context.getCanonical()
        if can != self.context:
            return can.UID()
        return ''
        
    def get_data(self):
        data = {}
        ## XXX: here we have to use an adapter
        schema = self.context.Schema()
        for i in schema.keys():
            value = self.context.getField(i).getAccessor(self.context)()
            if value is None:
                value = '[[None]]'
            data[i] = value
        return data
        
    def setProxy(self, proxy):
        """ used for testing currently..."""
        self.proxy = proxy
    
    @property   
    def rpc(self):
        server = self.context.REQUEST.get('server', None)
        if not server:
            return 
        proxy = ServerProxy(server)
        return proxy

    def getSiteId(self):
        """ set the site-id which identifies this site at the receving end 
        """
        return "/".join(self.context.portal_url.getPortalObject().getPhysicalPath())

    def getSyncStatus(self):
        """ return status about last synchronization """
        server = self.context.REQUEST.get('server', None)
        if not server:
            return "[No server specified]"
        return self.rpc.getSyncStatus(self.getSiteId(), self.context.UID())



    def syncObject(self, portal_type, data={}, remote_uid=None, translation_reference_uid=None):
        """ check if an object to the given remote_uid exists
            if not, create one using the portal_type
            update its data using the data mapping
            returns a feedback message and the link of the object in question
        """
        return self.rpc.syncObject(portal_type, data, self.getSiteId(), remote_uid, translation_reference_uid)

