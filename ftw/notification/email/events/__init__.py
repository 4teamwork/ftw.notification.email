from ftw.notification.email.interfaces import INotificationEmailSentEvent
from zope.component.interfaces import ObjectEvent
from zope.interface import implements


class NotificationEmailSentEvent(ObjectEvent):
    """Event fired when a notification email is sent.
    """
    implements(INotificationEmailSentEvent)

    def __init__(self, object, comment, to_userids, cc_userids):
        self.object = object
        self.comment = comment
        self.to_userids = to_userids
        self.cc_userids = cc_userids
