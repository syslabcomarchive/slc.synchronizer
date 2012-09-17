from zope.interface import implements

from persistent import Persistent
from BTrees.OOBTree import OOBTree

from slc.synchronizer.interfaces import IAccessStorage


class AccessStorage(Persistent):
    """Stores access credentials in an insecure manner into the portal.
    """
    implements(IAccessStorage)

    def __init__(self):
        self._data = OOBTree()

    def add(self, url, login, password):
        if not url or not login or not password:
            return
        self._data[(url, login)] = password

    def remove(self, url, login):
        del self._data[(url, login)]

    def has_key(self, url, login):
        return bool(self._data.has_key((url, login)))

    def get(self, url, login, default=None):
        return self._data.get((url, login), default)

    def __iter__(self):
        return iter(self._data)
