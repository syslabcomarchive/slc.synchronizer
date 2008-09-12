from Products.CMFCore.permissions import setDefaultRoles
GLOBALS = globals()

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    SynchronizeContent = 'Synchronize portal content'
    setDefaultRoles( SynchronizeContent, ( 'Manager', 'Owner' ) )