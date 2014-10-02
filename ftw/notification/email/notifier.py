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
from email.header import Header

logger = logging.getLogger('ftw.notification.email')

_marker = object()


class MailNotifier(BaseNotifier):

    def create_recipients(self, user_list):
        """Creates a unique list of recipients"""

        site = hooks.getSite()
        portal_membership = getToolByName(site, 'portal_membership')

        recipients = Header()

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
            recipients.append(fullname, 'utf-8')
            recipients.append(' <' + email + '>,')
        return recipients

    def send_notification(self, to_list=_marker, cc_list=_marker,
                          object_=None, message=u"", **kwargs):

        if to_list is _marker:
            to_list = []

        if cc_list is _marker:
            cc_list = []

        recipients = self.create_recipients(to_list)
        cc_recipients = self.create_recipients(cc_list)

        if not recipients:
            return

        actor = kwargs.get('actor', None)
        if actor:
            kwargs['sender'] = self.create_recipients([actor])
        else:
            kwargs['sender'] = ''

        if object_ is not None:
            try:
                subject = ISubjectCreator(object_)(object_)
                # Call attachment adapter
                attachments = IAttachmentCreator(object_)(object_)
                # subject should be utf-8
                if isinstance(subject, unicode):
                    subject = subject.encode('utf-8')
                subject = Header(subject, 'utf-8')
                email = IEMailRepresentation(object_)(subject,
                                                      recipients,
                                                      cc_recipients,
                                                      message,
                                                      attachments=attachments,
                                                      **kwargs)
                mailhost = getToolByName(object_, "MailHost")
                mailhost.send(
                    email)
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
