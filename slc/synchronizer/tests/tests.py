import os, sys

from slc.synchronizer import GLOBALS

import glob
from zope.testing import doctest
import unittest

from Globals import package_home
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from Products.CMFPlone.tests import PloneTestCase

import Products.Five.testbrowser
    
REQUIRE_TESTBROWSER = []

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

#PloneTestCase.installProduct('ATVocabularyManager')
#PloneTestCase.installProduct('RiskAssessmentLink')
#PloneTestCase.installProduct('RemoteProvider')
#PloneTestCase.setupPloneSite(products=['ATVocabularyManager','RiskAssessmentLink', 'RemoteProvider'])
PloneTestCase.setupPloneSite()

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
    print "test_suite", filenames

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
  