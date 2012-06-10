from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing import z2


class SlcSynchronizer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import slc.synchronizer
        self.loadZCML('configure.zcml', package=slc.synchronizer)

        z2.installProduct(app, 'Products.ZCatalog')
        z2.installProduct(app, 'slc.synchronizer')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'slc.synchronizer:default')

        # Login as manager and create a test folder
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        portal.invokeFactory('Folder', 'folder')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'Products.ZCatalog')
        z2.uninstallProduct(app, 'slc.synchronizer')


SLC_SYNCHRONIZER_FIXTURE = SlcSynchronizer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(SLC_SYNCHRONIZER_FIXTURE,),
    name="SlcSynchronizer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SLC_SYNCHRONIZER_FIXTURE,),
        name="SlcSynchronizer:Functional")
