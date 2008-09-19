import Acquisition, types
from zope.interface import implements
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from slc.synchronizer.interfaces import ISynchronizer, IAccessStorage, IDataExtractor
from xmlrpclib import ServerProxy
from zope.component import queryUtility
from persistent import Persistent
from zope.annotation.interfaces import IAnnotations
from AccessControl import Unauthorized

#XXX: Should also work without Linguaplone
try:
    from Products.LinguaPlone.interfaces import ITranslatable
    HAVE_LP = True
except:
    HAVE_LP = False    
    
ANNOKEY = "slc.synchronizer.data"    
    
class SyncSettings(Persistent):
    """ store sync status information 
    """    
    credentials = ''
    
        
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
        """ handle the form input
        """
        R = self.context.REQUEST
        if R.has_key('savecredentials') and R.get('savecredentials', '') != '':
            self._save_credentials()
            
        if R.has_key('form.button.Synchronize'):
            data = IDataExtractor(self.context)()                        
            self.syncObject(self.context.portal_type, 
                            data, 
                            remote_uid=self.context.UID(), 
                            translation_reference_uid=self.get_trans())
        return self.template() 


    def _save_credentials(self):
        """ save entered credentials into the storage, if the checkbox is checked
        """
        R = self.context.REQUEST
        server = R.get('server', '')
        username = R.get('username', '')
        password = R.get('password', '')
        storage = queryUtility(IAccessStorage)
        print "s, u, p", server, username, password
        storage.add(server, username, password)                


    def get_trans(self):        
        if not HAVE_LP or not ITranslatable.implementedBy(self.context):
            return ''
        can = self.context.getCanonical()
        if can != self.context:
            return can.UID()
        return ''
        
        
#    def get_data(self):
#        data = {}
#        ## XXX: here we have to use an adapter
#        schema = self.context.Schema()
#        for i in schema.keys():
#            value = self.context.getField(i).getAccessor(self.context)()
#            if value is None:
#                value = '[[None]]'
#            data[i] = value
#        return data
    
    def default_credentials(self):
        """ called by the form it checks if there is a credentials field in the request. 
            if not, it checks if we have a default credential key as annotation on the object
        """
        R = self.context.REQUEST
        if R.get('credentials', None):
            return R['credentials']  
        if self.syncsettings.credentials != '':
            return self.syncsettings.credentials
        return ''
    
    def _get_credentials(self):
        """ retrieve server, username and password from the environment 
        """
        R = self.context.REQUEST
        server = R.get('server', '')
        username = R.get('username', '')
        password = R.get('password', '')
        if not server or not username or not password:
            storage = queryUtility(IAccessStorage)
            if R.get('credentials', '') != '':
                login, server = R['credentials'].split('@', 1)
                password = storage.get(server, login, '')
            elif self.syncsettings.credentials != '':
                login, server = self.syncsettings.credentials.split('@', 1)
                password = storage.get(server, login, '')                
            else:
                return '', '', ''
        return server, login, password
            
            
    def _generate_target_url(self):
        """ generate an xmlrpc compatible url from the credentials 
        """
        server, login, password = self._get_credentials()  
        if not server or not login or not password:
            return ''
            
        if not server.startswith('http://'):
            server = "http://"+server
        if server[-1]=='/':
            server = server[:-1]

        targeturl = "http://%s:%s@%s/synchronize_receiver" % (login, password, server[7:])

        #print targeturl
        return targeturl
        
            
    @property   
    def rpc(self):
        """ connect to targeturl via xmlrpc
        """
        targeturl = self._generate_target_url()
        if not targeturl:
            return None
        proxy = ServerProxy(targeturl)
        return proxy
        

    def credentials(self):
        """ read existing credentials from the storage and display login and url as key
        """
        storage = queryUtility(IAccessStorage)
        for cred in storage:
            yield cred

       

    def getSiteId(self):
        """ set the site-id which identifies this site at the receving end 
        """
        return "/".join(self.context.portal_url.getPortalObject().getPhysicalPath())


    def getSyncStatus(self):
        """ return status about last synchronization """
        targeturl = self._generate_target_url()
        if not targeturl:
            return [-1, '']
                    
        try:
            syncstat = self.rpc.getSyncStatus(self.getSiteId(), self.context.UID())
            if syncstat[1]==-1:
                syncstat[1]=''
        except Unauthorized, uae:
            return [-1, 'Unauthorized: %s'%str(e)]
        except Exception, e:
            return [-1, 'Error: %s'%str(e)]
        else:
            return syncstat

    @property
    def syncsettings(self):
        ann = IAnnotations(self.context)
        return ann.setdefault(ANNOKEY, SyncSettings())

    def syncObject(self, portal_type, data={}, remote_uid=None, translation_reference_uid=None):
        """ check if an object to the given remote_uid exists
            if not, create one using the portal_type
            update its data using the data mapping
            returns a feedback message and the link of the object in question
        """
        syncstat = self.rpc.syncObject(portal_type, data, self.getSiteId(), remote_uid, translation_reference_uid)

        # if syncing was successful, remember the used credentials on this object
        server, login, password = self._get_credentials()
        if server and login:
            cred = "%s@%s" % (login, server)
            self.syncsettings.credentials = cred
            
        return syncstat

