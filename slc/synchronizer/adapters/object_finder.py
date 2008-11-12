from zope.interface import implements
from zope.app.component.hooks import getSite
from slc.synchronizer.interfaces import IObjectFinder

ILLEGAL_CHARS =['(', ')', '-', '/', '\\', '+', '[', ']', '*', '#', '$', '%',]


class ObjectFinder(object):
    """Finds an object based on some algorithms
    """
    implements(IObjectFinder)
    
    def __call__(self, data, portal_type):
        portal = getSite()
        pc = portal.portal_catalog
        title = data.get('title')
        search_title = title
        for char in ILLEGAL_CHARS:
            search_title = search_title.replace(char, ' ')
        results = pc(portal_type=portal_type, Title=search_title, Language='all')
        if len(results)==1:
            try:
                target_title = unicode(results[0].Title, 'utf-8')
            except:
                return None
            if title == target_title:
                return results[0].getObject()
        elif len(results)>1:
            possible_results = list()
            for res in results:
              try:
                if unicode(res.Title, 'utf-8') == title:
                    possible_results.append(res)
              except Exception, err:
                print "ObjectFinder - Error in trying to compare titles: %s" %err
            if len(possible_results)==1:
                return possible_results[0].getObject()
        return None
        
