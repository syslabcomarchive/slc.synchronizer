import os, sys

from slc.synchronizer import GLOBALS

import glob
from zope.testing import doctest
import unittest

from Globals import package_home
from Testing import ZopeTestCase as ztc
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from Products.CMFPlone.tests import PloneTestCase
from Products.PloneTestCase.layer import onsetup
from Products.Five import zcml
from Products.Five import fiveconfigure
import Products.Five.testbrowser
    
REQUIRE_TESTBROWSER = []

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


@onsetup
def setup_product():
    """Set up the package and its dependencies.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer. We could have created our
    own layer, but this is the easiest way for Plone integration tests.
    """
    
    # Load the ZCML configuration for the example.tests package.
    # This can of course use <include /> to include other packages.
    
    fiveconfigure.debug_mode = True
    import slc.synchronizer
    zcml.load_config('configure.zcml', slc.synchronizer)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML. Thus, we do it here. Note the use of installPackage() instead
    # of installProduct().
    # 
    # This is *only* necessary for packages outside the Products.* namespace
    # which are also declared as Zope 2 products, using 
    # <five:registerPackage /> in ZCML.
    
    # We may also need to load dependencies, e.g.:
    # 
    #   ztc.installPackage('borg.localrole')
    # 
    
    ztc.installPackage('slc.synchronizer')
    
# The order here is important: We first call the (deferred) function which
# installs the products we need for this product. Then, we let PloneTestCase 
# set up this product on installation.

setup_product()
PloneTestCase.setupPloneSite(products=['slc.synchronizer'])

from zope.interface import implements

from zope.annotation import IAttributeAnnotatable
from zope.publisher.browser import TestRequest as ZopeTestRequest
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.interfaces.browser import IBrowserRequest
	
class TestRequest(ZopeTestRequest):
    implements(IHTTPRequest, IAttributeAnnotatable, IBrowserRequest)
	
    def set(self, attribute, value):
        self._environ[attribute] = value

def list_doctests():
    home = package_home(GLOBALS)
    return [filename for filename in
            glob.glob(os.path.sep.join([home, 'tests', '*.txt']))]

def list_nontestbrowser_tests():
    return [filename for filename in list_doctests()
            if os.path.basename(filename) not in REQUIRE_TESTBROWSER]

def test_suite():
    filenames = list_doctests()

    suites = [Suite(os.path.sep.join(['tests', os.path.basename(filename)]),
                    optionflags=OPTIONFLAGS,
                    package='slc.synchronizer',
                    test_class=PloneTestCase.FunctionalTestCase)
              for filename in filenames]


    # BBB: Fix for http://zope.org/Collectors/Zope/2178
    from Products.PloneTestCase import layer
    from Products.PloneTestCase import setup

    if setup.USELAYER:
        for s in suites:
            if not hasattr(s, 'layer'):
                s.layer = layer.PloneSite

    return unittest.TestSuite(suites)
  