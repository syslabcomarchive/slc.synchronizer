from zope.interface import implements
from zope.app.component.hooks import getSite
from slc.synchronizer.interfaces import IObjectFinder

class ObjectFinder(object):
    """Finds an object based on some algorithms
    """
    implements(IObjectFinder)
    
    def __call__(self, data):
        portal = getSite()
        pc = portal.portal_catalog
        title = data.get('title')
        portal_type = data.get('portal_type')
        results = pc(portal_type=portal_type, title=title, Language='all')
        print "ObjectFinder found %s hits" % len(results)
        if len(results)==1:
            return results[0].getObject()
        return None
        