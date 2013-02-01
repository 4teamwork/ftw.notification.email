from ftw.notification.base import notification_base_factory as _nb
from ftw.notification.base.notifier import BaseNotifier
from ftw.notification.email.interfaces import (
    IEMailRepresentation, ISubjectCreator, IAttachmentCreator)
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from StringIO import StringIO
from ZODB.POSException import ConflictError
from zope.component import hooks
from zope.publisher.interfaces import Retry
import logging
import sys
import traceback


logger = logging.getLogger('ftw.notification.email')

_marker = object()


class MailNotifier(BaseNotifier):

    def create_recipients(self, user_list):
        """Creates a unique list of recipients"""

        site = hooks.getSite()
        portal_membership = getToolByName(site, 'portal_membership')

        recipients = {}

        for user_id in user_list:
            member = portal_membership.getMemberById(user_id)
            if member is None:
                continue
            fullname = member.getProperty('fullname', user_id)
            if not len(fullname):
                fullname = user_id
            email = member.getProperty('email', None)
            if email is None:
                continue
            recipients[user_id] = (fullname, email)
        return recipients

    def send_notification(self, to_list=_marker, cc_list=_marker,
                          object_=None, message=u"", **kwargs):

        if to_list is _marker:
            to_list = []

        if cc_list is _marker:
            cc_list = []

        site = hooks.getSite()
        portal_membership = getToolByName(object_ or site, 'portal_membership')

        recipients = self.create_recipients(to_list)
        cc_recipients = self.create_recipients(cc_list)

        if not recipients:
            return

        sender = None
        sender_id = kwargs.get('actor', '')
        sender_data = portal_membership.getMemberById(sender_id)
        if sender_data is not None:
            sender_fullname = sender_data.getProperty('fullname', sender_id)
            if not len(sender_fullname):
                sender_fullname = sender_id
            sender_email = sender_data.getProperty('email', '')
            sender = (sender_fullname, sender_email)
        kwargs.update(dict(sender=sender))
        if object_ is not None:
            try:
                subject = ISubjectCreator(object_)(object_)
                # Call attachment adapter
                attachments = IAttachmentCreator(object_)(object_)
                # subject should be utf-8
                if isinstance(subject, unicode):
                    subject = subject.encode('utf-8')
                email = IEMailRepresentation(object_)(subject,
                                                      recipients.values(),
                                                      cc_recipients.values(),
                                                      message,
                                                      attachments=attachments,
                                                      **kwargs)
                mailhost = getToolByName(object_, "MailHost")

                # XXX: Unfortunality we have to implement the carbon copy
                # feature by ourself.
                to_addr = []
                if email['To']:
                    to_addr.append(email['To'])
                if email['CC']:
                    to_addr.append(email['CC'])
                to_addr = ','.join(to_addr)

                mailhost.send(
                    email.as_string(), to_addr, email['From'], subject)
                IStatusMessage(object_.REQUEST).addStatusMessage(
                        _nb('statusmessage_notification_sent'), type='info')
            except (ConflictError, Retry):
                raise
            except Exception, error:
                exceptionType, exceptionValue, exceptionTraceback = \
                                                            sys.exc_info()
                exs = StringIO()
                print error
                exs.write('Error while sending notification\n')
                traceback.print_exception(exceptionType, exceptionValue,
                                          exceptionTraceback, file=exs)
                exs.seek(0)
                logger.error(exs.read())
                IStatusMessage(object_.REQUEST).addStatusMessage(
                    _nb('statusmessage_notification_not_sent'), type='error')
