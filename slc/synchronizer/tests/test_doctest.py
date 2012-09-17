import doctest
import unittest2 as unittest

from slc.synchronizer.tests.tests import FUNCTIONAL_TESTING
from plone.testing import layered

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


TESTFILES = [
    'push_content.txt',
    'receiver.txt'
]


def test_suite():
    suite  = unittest.TestSuite()
    suite.addTests([
        layered(
                doctest.DocFileSuite(
                    docfile,
                    optionflags=OPTIONFLAGS),
                layer=FUNCTIONAL_TESTING)
         for docfile in TESTFILES
    ])
    return suite
