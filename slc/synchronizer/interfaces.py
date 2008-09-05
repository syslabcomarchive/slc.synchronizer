from zope.interface import Interface

class IReceiver(Interface):
    """ Interface for a component that receives data from a remote site to add objects to this site
    """
    
    def getSyncStatus(site_id, remote_uid):
        """ looks up the remote uid in the local utility to get the local uid.
            resolves the object using the local uid
            returns the modification date of the referenced object or None, if no such object exists
            as well as the link of the object
        """

    def syncObject(portal_type, data={}, site_id, remote_uid=None, translation_reference_uid=None):
        """ check if an object to the given remote_uid exists
            if not, create one using the portal_type
            update its data using the data mapping
            returns a feedback message and the link of the object in question
        """
        
    
class IUIDMappingStorage(Interface):
    """ A storage for uids which maps a remote uid and a remote site identifier to a 
        local uid 
        registered as a local utility.
    """

    def add(site_id, remote_uid, local_uid):
        """registers a skinname for the path of a subsite
           updating if path exists
        """
        
    def remove(site_id, remote_uid):
        """Forget the remote uid for a site
        """

    def has_remote_uid(site_id, remote_uid):
        """Check if we have a registration
        """
        
    def get(site_id, remote_uid, default=None):
        """Get the local uid for a given site and remote_uid
        Will return None if nothing found 
        """

    def __iter__():
        """Iterate over all existing subsite paths."""            
        

class ISynchronizer(Interface):
    """ Interface for synchronization functionality """


class IDataExtractor(Interface):
    """ Interface for an adapter that extracts the content of object and returns
        it as a key-value-mapping
    """
    
    