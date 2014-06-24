from unittest2 import TestCase
from zope.component import getUtility
from ftw.notification.email.testing import NOTIFICATION_INTEGRATION_TESTING
from ftw.notification.base.interfaces import INotifier
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing.mailing import Mailing
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from ftw.notification.base.events.events import NotificationEvent
from zope.event import notify
from zope.annotation.interfaces import IAnnotations
from zope.component import eventtesting


class TestEvents(TestCase):
    
    layer = NOTIFICATION_INTEGRATION_TESTING

    def setUp(self):
        super(TestEvents, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        login(self.portal, TEST_USER_NAME)
        Mailing(self.portal).set_up()
        eventtesting.setUp()
        self.user1 = create(Builder('user'))
        self.user2 = create(Builder('user').named("Hans","Muster"))
        self.file = create(Builder('file'))

    def tearDown(self):
        Mailing(self.portal).tear_down()

    def test_notification_sent_mail(self):
        self.request['to_list'] = ['john.doe']
        notify(NotificationEvent(self.file, u'blubber'))
        mail = Mailing(self.portal).pop()
        self.assertIn('=?utf-8?q?=5BPlone_site=5D_Notification=3A_?=', mail)
        self.assertIn(' =?utf-8?q?Doe_John?=  <john@doe.com>', mail)