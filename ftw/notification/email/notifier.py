from izug.notification.base.notifier import IZugBaseNotifier
from zope.sendmail.delivery import DirectMailDelivery
from zope.sendmail.mailer import SMTPMailer
from zope.sendmail.interfaces import IMailer
from zope.interface import implements
import logging
logger = logging.getLogger('izug.notification.email')

class MailerStub(object):

    implements(IMailer)
    def __init__(self, *args, **kw):
        self.sent_messages = []

    def send(self, fromaddr, toaddrs, message):
        self.sent_messages.append((fromaddr, toaddrs, message))


class IZugMailNotifier(IZugBaseNotifier):
    def send_notification(self, to_list=[], cc_list=[], object=None, message=u"", **kwargs):
        logger.info("message sent to outer space...")
        return 1
        mailer = SMTPMailer(hostname=object.MailHost.smtp_host, 
                            username=object.MailHost.smtp_userid, 
                            password=object.MailHost.smtp_pass)
                            
        delivery = DirectMailDelivery(mailer)
        fromaddr = "Info <info@4teamwork.ch>"
        toaddrs = ('Victor Baumann <v.baumann@4teamwork.ch>',)
        opt_headers = ('From: Victor Baumann <v.baumann@4teamwork.ch>\n'
                       'To: Victor Baumann <v.baumann@4teamwork.ch>:;\n'
                       'Message-Id: <20030519.1234@example.org>\n')
        message =     ('Subject: example\n'
                       '\n'
                       '%s' % message)

        msgid = delivery.send(fromaddr, toaddrs, opt_headers + message)
        return str(self.__class__)
