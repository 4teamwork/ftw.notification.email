import doctest
from plone.testing import layered
import unittest2 as unittest
from ftw.notification.email.testing import NOTIFICATION_INTEGRATION_TESTING


OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF)


TESTFILES = (
    'notification.txt',
    )



def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([layered(doctest.DocFileSuite(filename,
                                                 optionflags=OPTIONFLAGS),
                    layer=NOTIFICATION_INTEGRATION_TESTING)
                    for filename in TESTFILES])
    return suite