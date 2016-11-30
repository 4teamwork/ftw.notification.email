from unittest2 import TestCase
from zope.component import getUtility
from ftw.notification.email.testing import NOTIFICATION_INTEGRATION_TESTING
from ftw.notification.base.interfaces import INotifier
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing.mailing import Mailing
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from Products.CMFCore.utils import getToolByName

class TestFormatEmail(TestCase):

    layer = NOTIFICATION_INTEGRATION_TESTING

    def setUp(self):
        super(TestFormatEmail, self).setUp()
        self.portal = self.layer['portal']
        login(self.portal, TEST_USER_NAME)
        Mailing(self.portal).set_up()
        self.notifier = getUtility(INotifier, name="email-notifier", context=self.portal)
        self.user1 = create(Builder('user'))
        self.user2 = create(Builder('user').named("Hans","Muster"))
        self.file = create(Builder('file'))

    def tearDown(self):
        Mailing(self.portal).tear_down()


    def test_format_single(self):
        receiver = self.notifier.create_recipients(['john.doe'])
        self.assertEqual('=?utf-8?q?Doe_John?=  <john@doe.com>,', str(receiver))

    def test_format_multiple(self):
        receiver = self.notifier.create_recipients(['john.doe', 'hans.muster'])
        self.assertEqual('=?utf-8?q?Doe_John?=  <john@doe.com>, =?utf-8?q?Muster_Hans?=\n <hans@muster.com>,', str(receiver))

    def test_send_notification(self):
        self.notifier.send_notification(to_list=['john.doe'], cc_list=['hans.muster'], object_=self.file, message=u'hallo velo')
        Mailing(self.portal).pop()

    def test_correct_subject(self):
        self.notifier.send_notification(to_list=['john.doe'], cc_list=['hans.muster'], object_=self.file, message=u'hallo velo')
        mail = Mailing(self.portal).pop()
        self.assertIn('=?utf-8?q?=5BPlone_site=5D_Notification=3A_?=', mail)

    def test_correct_receiver(self):
        self.notifier.send_notification(to_list=['john.doe'], cc_list=['hans.muster'], object_=self.file, message=u'hallo velo')
        mail = Mailing(self.portal).pop()
        self.assertIn('To: =?utf-8?q?Doe_John?=  <john@doe.com>', mail)

    def test_actor_is_used_for_reply_to_header(self):
        self.notifier.send_notification(to_list=['john.doe'],
                                        cc_list=['hans.muster'], object_=
                                        self.file,
                                        message=u'hallo velo',
                                        actor='john.doe')
        mail = Mailing(self.portal).pop()
        self.assertIn('Reply-To: =?utf-8?q?Doe_John?=  <john@doe.com>', mail)

    def test_correct_multiple_receiver_41(self):
        migration_tool = getToolByName(self, 'portal_migration')
        if not migration_tool.getInstanceVersion().startswith('41'):
            return
        self.notifier.send_notification(to_list=['john.doe', 'hans.muster'], object_=self.file, message=u'hallo velo')
        mail = Mailing(self.portal).pop()
        self.assertIn('To: =?utf-8?q?Doe_John?=  <john@doe.com>, =?utf-8?q?Muster_Hans?=\n\t<hans@muster.com>', mail)

    def test_correct_multiple_receiver_42_3(self):
        migration_tool = getToolByName(self, 'portal_migration')
        if migration_tool.getInstanceVersion().startswith('41'):
            return
        self.notifier.send_notification(to_list=['john.doe', 'hans.muster'], object_=self.file, message=u'hallo velo')
        mail = Mailing(self.portal).pop()
        self.assertIn('To: =?utf-8?q?Doe_John?=  <john@doe.com>, =?utf-8?q?Muster_Hans?=\n <hans@muster.com>', mail)

    def test_correct_cc(self):
        self.notifier.send_notification(to_list=['john.doe'], cc_list=['hans.muster'], object_=self.file, message=u'hallo velo')
        mail = Mailing(self.portal).pop()
        self.assertIn('CC: =?utf-8?q?Muster_Hans?=  <hans@muster.com>', mail)

    def test_comment_in_email(self):
        self.notifier.send_notification(to_list=['john.doe'], cc_list=['hans.muster'], object_=self.file, message=u'hallo velo')
        mail = Mailing(self.portal).pop()
        self.assertIn('hallo velo', mail)

    def test_link_in_email(self):
        self.notifier.send_notification(to_list=['john.doe'], cc_list=['hans.muster'], object_=self.file, message=u'hallo velo')
        mail = Mailing(self.portal).pop()
        self.assertIn('href=3D"http://nohost/plone/file"', mail)
