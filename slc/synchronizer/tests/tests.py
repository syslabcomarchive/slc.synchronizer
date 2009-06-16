from Globals import package_home
from Products.CMFPlone.tests import PloneTestCase
from Products.Five import fiveconfigure, zcml
from Products.PloneTestCase import layer
from Products.PloneTestCase.layer import onsetup, onsetup
from Testing import ZopeTestCase as ztc
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from slc.synchronizer import GLOBALS
from zope.annotation import IAttributeAnnotatable
from zope.interface import implements
from zope.publisher.browser import TestRequest as ZopeTestRequest
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.http import IHTTPRequest
from zope.testing import doctest
import Products.Five.testbrowser
import glob
import os
import sys
import unittest

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

SiteLayer = layer.PloneSite

class SynchronizerLayer(SiteLayer):
    @classmethod
    def setUp(cls):
        """Set up additional products and ZCML required to test this product.
        """
        ztc.installProduct('ZCatalog')
        PloneTestCase.setupPloneSite(products=['slc.synchronizer'])
        fiveconfigure.debug_mode = True
        import slc.synchronizer
        zcml.load_config('configure.zcml', slc.synchronizer)
        fiveconfigure.debug_mode = False
        ztc.installPackage('slc.synchronizer')
        SiteLayer.setUp()

class TestCase(PloneTestCase.FunctionalTestCase):
    layer = SynchronizerLayer

def list_doctests():
    home = package_home(GLOBALS)
    return [filename for filename in
            glob.glob(os.path.sep.join([home, 'tests', '*.txt']))]

def test_suite():
    filenames = list_doctests()

    suites = [Suite(os.path.sep.join(['tests', os.path.basename(filename)]),
                    optionflags=OPTIONFLAGS,
                    package='slc.synchronizer',
                    test_class=TestCase)
              for filename in filenames]


    return unittest.TestSuite(suites)
