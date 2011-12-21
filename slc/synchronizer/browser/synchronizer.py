# -*- coding: utf-8 -*-
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
from DateTime import DateTime
import logging

logger = logging.getLogger('slc.synchronizer')

#XXX: Should also work without Linguaplone - untested
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
    last_synchronized = ''


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
        context = Acquisition.aq_inner(self.context)
        R = context.REQUEST
        putil = getToolByName(context, 'plone_utils')
        log = putil.addPortalMessage
        pc = getToolByName(context, 'portal_catalog')

        if R.has_key('savecredentials') and R.get('savecredentials', '') != '':
            self._save_credentials()
            log("Credentials saved" , 'info')

        if R.has_key('form.button.Synchronize'):
            refs = pc(Language='all', UID=R.get('refs'))
            trans = pc(Language='all', UID=R.get('trans'))

            refs = [x.getObject() for x in refs]
            trans = [x.getObject() for x in trans]
            obs = refs + [context] + trans
            for ob in obs:
                # Here the magic happens. IDataExtractor reads all
                # attributes from the object and modifies them so that
                # the target site can create an object from them
                # This adapter needs to make sure, the contract of the
                # targetsite is fulfilled. To be able to do that, the adapter
                # might need to be site specific.
                extractor = IDataExtractor(ob)
                syncstatus = self.syncObject(extractor.portal_type(),
                                             extractor.data(),
                                             remote_uid=ob.UID(),
                                             translation_reference_uid=self._get_trans(ob))
                if syncstatus[0]==0:
                    log("%s - URL: %s" %(syncstatus[1], syncstatus[2]), 'info')
                elif syncstatus[0]==1:
                    log("%s - URL: %s" %(syncstatus[1], syncstatus[2]), 'warning')
                else:
                    log("%s - URL: %s" %(syncstatus[1], syncstatus[2]), 'error')

        elif R.has_key('form.button.Status'):
            log("Status updated", 'info')
        elif R.has_key('form.button.DeleteCredentials'):
            if R.has_key('credentials'):
                self._delete_credentials(R.get('credentials'))
                log("Credentials deleted", 'info')
            else:
                log("No credentials selected. Nothing has been deleted", 'warning')

        return self.template()

    def _delete_credentials(self, credentials):
        """ delete selected credentials from the storage """
        storage = queryUtility(IAccessStorage)
        username, server = credentials.rsplit('@', 1)
        storage.remove(server, username)

    def _save_credentials(self):
        """ save entered credentials into the storage, if the checkbox is checked
        """
        R = self.context.REQUEST
        server = R.get('server', '')
        username = R.get('username', '')
        password = R.get('password', '')
        storage = queryUtility(IAccessStorage)
        storage.add(server, username, password)

    def _get_trans(self, ob):
        if not HAVE_LP or not ITranslatable.providedBy(ob):
            return ''
        can = ob.getCanonical()
        if can != ob:
            return can.UID()
        return ''

    def getLastSync(self):
        return self.syncsettings.last_synchronized

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
                username, server = R['credentials'].rsplit('@', 1)
                password = storage.get(server, username, '')
            elif self.syncsettings.credentials != '':
                username, server = self.syncsettings.credentials.rsplit('@', 1)
                password = storage.get(server, username, '')
            # elif self.portal_syncsettings.credentials !='':
            #     #check if there is a global credential default
            #     username, server = self.portal_syncsettings.credentials.rsplit('@', 1)
            #     password = storage.get(server, username, '')
            else:
                return '', '', ''
        return server, username, password

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
            HARD-CODED for GFB
        """
        return "/osha/gfb"

    def getReferences(self):
        """ retrieve all objects which are referenced by this object
        """
        pw = getToolByName(self.context, 'portal_workflow')
        fields = self.context.Schema().fields()
        refs = []
        for field in fields:
            fname = field.getName()
            ftype = field.getType()
            if ftype == 'Products.Archetypes.Field.ReferenceField':
                for item in field.getAccessor(self.context)():
                    refs.append((item, pw.getCatalogVariablesFor(item).get('review_state', ''), fname))
        return refs

    def getSyncStatus(self, uid=''):
        """ return status about last synchronization """
        if not uid:
            uid = self.context.UID()
        targeturl = self._generate_target_url()
        if not targeturl:
            return [-1, '']

        try:
            syncstat = self.rpc.getSyncStatus(self.getSiteId(), uid)
            if syncstat[1]==-1:
                syncstat[1]=''
            if syncstat[0]!=-1:
                syncstat[0] = DateTime(syncstat[0])
        except Unauthorized, e:
            return [-1, 'Unauthorized: %s'%str(e)]
        except Exception, e:
            return [-1, 'Error: %s'%str(e)]
        else:
            return syncstat

    @property
    def syncsettings(self):
        ann = IAnnotations(self.context)
        return ann.setdefault(ANNOKEY, SyncSettings())

    # @property
    # def portal_syncsettings(self):
    #     ann = IAnnotations(self.context.portal_url.getPortalObject())
    #     return ann.setdefault(ANNOKEY, SyncSettings())

    def syncObject(self, portal_type,
                         data={},
                         remote_uid=None,
                         translation_reference_uid=None):
        """ check if an object to the given remote_uid exists
            if not, create one using the portal_type
            update its data using the data mapping
            returns a feedback message and the link of the object in question
        """
        logger.info("Synchronizing %s, remote_uid %s, translation %s" %(portal_type, remote_uid, translation_reference_uid))
        try:
            syncstat = self.rpc.syncObject(portal_type, data, self.getSiteId(), remote_uid, translation_reference_uid)
        except Exception, e:
            return (2, str(e), '')
        # if syncing was successful, remember the used credentials on this object
        server, login, password = self._get_credentials()
        if server and login:
            cred = "%s@%s" % (login, server)
            self.syncsettings.credentials = cred
            self.syncsettings.last_synchronized = DateTime()

        return syncstat
