from zope.interface import implements

from persistent import Persistent
from BTrees.OOBTree import OOBTree, OOSet

from slc.synchronizer.interfaces import IUIDMappingStorage

class UIDMappingStorage(Persistent):
    """Stores a mapping between remote uids and local uids.
    """
    implements(IUIDMappingStorage)
    
    def __init__(self):
        self._uidmap = OOBTree()
    
    def add(self, site_id, remote_uid, local_uid):
        if not site_id or not remote_uid or not local_uid:
            return
            
        self._uidmap[(site_id, remote_uid)] = local_uid
        
    def remove(self, site_id, remote_uid):
        del self._uidmap[(site_id, remote_uid)]
        
    def has_remote_uid(self, site_id, remote_uid):
        return bool(self._uidmap.has_key((site_id, remote_uid)))

    def get(self, site_id, remote_uid, default=None):
        return self._uidmap.get((site_id, remote_uid), default)

    def __iter__(self):
        return iter(self._uidmap)
