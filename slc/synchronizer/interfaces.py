from zope.interface import Interface

class IReceiver(Interface):
    """ Interface for a component that receives data from a remote site to add objects to this site
    """
    
    def getSyncStatus(remote_uid):
        """ looks up the remote uid in the local utility to get the local uid.
            resolves the object using the local uid
            returns the modification date of the referenced object or None, if no such object exists
            as well as the link of the object
        """

    def syncObject(portal_type, data={}, remote_uid=None, translation_reference_uid=None):
        """ check if an object to the given remote_uid exists
            if not, create one using the portal_type
            update its data using the data mapping
            returns a feedback message and the link of the object in question
        """


class ISynchronizer(Interface):
    """ Interface for synchronization functionality """