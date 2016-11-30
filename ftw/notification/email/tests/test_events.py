from ftw.builder import Builder
from ftw.builder import create
from ftw.notification.base.events.events import NotificationEvent
from ftw.notification.email.events import NotificationEmailSentEvent
from ftw.notification.email.interfaces import INotificationEmailSentEvent
from ftw.notification.email.testing import NOTIFICATION_INTEGRATION_TESTING
from ftw.testing.mailing import Mailing
from unittest2 import TestCase
from zope.component import eventtesting
from zope.event import notify


class TestEvents(TestCase):
    layer = NOTIFICATION_INTEGRATION_TESTING

    def setUp(self):
        super(TestEvents, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        Mailing(self.portal).set_up()
        eventtesting.setUp()

    def tearDown(self):
        Mailing(self.portal).tear_down()

    def test_notification_sent_mail(self):
        john = create(Builder('user').named('John', 'Doe'))
        hugo = create(Builder('user').named('Hugo', 'Boss'))
        file_ = create(Builder('file'))

        comment = u'Hall\xf6chen, schaut mal, das ist ne interssante Datei.'
        self.request['to_list'] = [john.getId()]
        self.request['cc_list'] = [hugo.getId()]
        notify(NotificationEvent(file_, comment))

        mail = Mailing(self.portal).pop()
        self.assertIn('=?utf-8?q?=5BPlone_site=5D_Notification=3A_?=', mail)
        self.assertIn(' =?utf-8?q?Doe_John?=  <john@doe.com>', mail)
        self.assertIn(' =?utf-8?q?Boss_Hugo?=  <hugo@boss.com>', mail)

        events = eventtesting.getEvents(INotificationEmailSentEvent)
        self.assertEquals([NotificationEmailSentEvent], map(type, events))
        event, = events
        self.assertEquals(file_, event.object)
        self.assertEquals(comment, event.comment)
        self.assertEquals([john.getId()], event.to_userids)
        self.assertEquals([hugo.getId()], event.cc_userids)
