from zope.i18nmessageid import MessageFactory

emailNotificationMessageFactory = MessageFactory('ftw.notification.email')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
