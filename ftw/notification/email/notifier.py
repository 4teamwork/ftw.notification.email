from StringIO import StringIO
from ftw.notification.base.notifier import BaseNotifier
from zope.sendmail.delivery import DirectMailDelivery
from zope.sendmail.mailer import SMTPMailer
from zope.sendmail.interfaces import IMailer
from zope.app.component import hooks
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from ftw.sendmail.composer import HTMLComposer
import logging
from zope import component
from zope.sendmail.interfaces import IMailer
from ftw.notification.email.interfaces import IEMailRepresentation
from ftw.notification.base import notification_base_factory as _
from Products.statusmessages.interfaces import IStatusMessage
from zope.publisher.interfaces import Retry
from ZODB.POSException import ConflictError 
import traceback
import sys
logger = logging.getLogger('izug.notification.email')

class MailNotifier(BaseNotifier):
    def send_notification(self, to_list=[], cc_list=[], object_=None, message=u"", **kwargs):
        #XXX. cc_list not implemented
        site = hooks.getSite()
        portal_membership = getToolByName(object_ or site, 'portal_membership')

        recipients = {}
        
        for user_id in to_list:
            member = portal_membership.getMemberById(user_id)
            if member is None:
                continue
            fullname = member.getProperty('fullname', user_id)
            if not len(fullname):
                fullname = user_id
            email =  member.getProperty('email', None)
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
            sender_email =  sender_data.getProperty('email', '')  
            sender = (sender_fullname, sender_email)      
        kwargs.update(dict(sender=sender))
        if object_ is not None:
            try:
                #XXX translate...
                email = IEMailRepresentation(object_)('[iZug] Benachrichtigung', recipients.values(), message, **kwargs)
                smtp = component.getUtility(IMailer, 'plone.smtp')
                smtp.update_settings()
                smtp.send(email['From'], email['To'], email.as_string())
                IStatusMessage(object_.request).addStatusMessage(_('statusmessage_notification_sent'), type='info')
            except (ConflictError, Retry):
                raise
            except Exception, error:
                exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                exs = StringIO()
                exs.write('Error while sending notification\n')
                traceback.print_exception(exceptionType, exceptionValue, exceptionTraceback, file=exs)
                exs.seek(0)
                logger.error(exs.read())
                IStatusMessage(object_.request).addStatusMessage(_('statusmessage_notification_not_sent'), type='error')
                
