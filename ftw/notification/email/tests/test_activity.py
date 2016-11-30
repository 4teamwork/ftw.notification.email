from ftw.activity.tests.helpers import get_soup_activities
from ftw.activity.tests.pages import activity
from ftw.builder import Builder
from ftw.builder import create
from ftw.notification.base.events.events import NotificationEvent
from ftw.notification.email.testing import NOTIFICATION_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testing.mailing import Mailing
from unittest2 import TestCase
from zope.event import notify
import transaction


class TestActivity(TestCase):
    layer = NOTIFICATION_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestActivity, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        Mailing(self.portal).set_up()

    def tearDown(self):
        Mailing(self.portal).tear_down()

    @browsing
    def test_notification_sent_mail(self, browser):
        john = create(Builder('user').named('John', 'Doe'))
        hugo = create(Builder('user').named('Hugo', 'Boss'))
        file_ = create(Builder('file'))

        comment = u'Hall\xf6chen, schaut mal, das ist ne interssante Datei.'
        self.request['to_list'] = [john.getId()]
        self.request['cc_list'] = [hugo.getId()]
        notify(NotificationEvent(file_, comment))

        self.maxDiff = None
        self.assertEquals(
            [
                {'action': 'added',
                 'actor': 'test_user_1_',
                 'path': '/plone/file'},

                {'action': 'notification:email_sent',
                 'actor': 'test_user_1_',
                 'path': '/plone/file',
                 'notification:comment': comment,
                 'notification:to_userids': ('john.doe', ),
                 'notification:cc_userids': ('hugo.boss', ),
                },
            ],

            get_soup_activities(('path',
                                 'action',
                                 'actor',
                                 'notification:comment',
                                 'notification:to_userids',
                                 'notification:cc_userids')))
        transaction.commit()

        browser.open(file_, view='@@activity')
        newest_event = activity.events()[0]
        self.assertEquals(
            {'url': 'http://nohost/plone/file/view',
             'byline': 'Notification sent now by test_user_1_',
             'title': ''},
            newest_event.infos())
        self.assertEquals(
            u'TO: Doe John'
            u' CC: Boss Hugo'
            u' Comment: ' + comment,
            newest_event.body_text)
