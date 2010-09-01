from StringIO import StringIO
from ftw.notification.base.notifier import BaseNotifier
from zope.app.component import hooks
from Products.CMFCore.utils import getToolByName
import logging
from ftw.notification.email.interfaces import IEMailRepresentation
from ftw.notification.base import notification_base_factory as _
from Products.statusmessages.interfaces import IStatusMessage
from zope.publisher.interfaces import Retry
from ZODB.POSException import ConflictError
import traceback
import sys
logger = logging.getLogger('izug.notification.email')


class MailNotifier(BaseNotifier):

    def send_notification(self, to_list=[], cc_list=[], object_=None,
                          message=u"", **kwargs):
        #XXX. cc_list not implemented
        site = hooks.getSite()
        portal_membership = getToolByName(object_ or site, 'portal_membership')
        portal_properties = getToolByName(object_ or site, 'portal_properties')

        recipients = {}

        for user_id in to_list:
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
                default_subject = '[%s] Notification' % site.Title()
                subject = None
                try:
                    sheet = portal_properties.ftw_notification_properties
                except AttributeError:
                    subject = default_subject
                else:
                    subject = sheet.getProperty('notification_email_subject',
                                                default_subject)
                email = IEMailRepresentation(object_)(subject,
                                                      recipients.values(),
                                                      message, **kwargs)
                mailhost = getToolByName(object_, "MailHost")
                mailhost.send(email.as_string(), email['To'], email['From'], subject)
                IStatusMessage(object_.REQUEST).addStatusMessage(
                        _('statusmessage_notification_sent'), type='info')
            except (ConflictError, Retry):
                raise
            except Exception, error:
                exceptionType, exceptionValue, exceptionTraceback = \
                                                            sys.exc_info()
                exs = StringIO()
                import pdb; pdb.set_trace( )
                exs.write('Error while sending notification\n')
                traceback.print_exception(exceptionType, exceptionValue,
                                          exceptionTraceback, file=exs)
                exs.seek(0)
                logger.error(exs.read())
                IStatusMessage(object_.REQUEST).addStatusMessage(
                    _('statusmessage_notification_not_sent'), type='error')
