from zope.interface import implements
from zope.app.component.hooks import getSite
from slc.synchronizer.interfaces import IObjectFinder

class ObjectFinder(object):
    """Finds an object based on some algorithms
    """
    implements(IObjectFinder)
    
    def __call__(self, data, portal_type):
        portal = getSite()
        pc = portal.portal_catalog
        title = data.get('title')
        results = pc(portal_type=portal_type, Title=title, Language='all')
        if len(results)==1:
            return results[0].getObject()
        return None
        
