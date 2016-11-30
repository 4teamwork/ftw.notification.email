# pylint: disable=E0211, E0213
# E0211: Method has no argument
# E0213: Method should have "self" as first argument

from ftw.notification.base.interfaces import INotifier
from zope.component.interfaces import IObjectEvent
from zope.interface import Attribute
from zope.interface import Interface


class IFormatItem(Interface):
    """A view that formats an item for use in a notification.

    Given an item as retrieved from a collector, this view returns a
    representation of the given item ready for inclusion in the
    message via the ``IComposer.render`` method.
    """

    def __call__():
        """Returns a unicode-string."""


class IEMailComposer(Interface):
    """An email composer.
    """


class ISubjectCreator(Interface):
    """Interface for
    """


class IMailNotifier(INotifier):
    """Interface for
    """


class IAttachmentCreator(Interface):
    """Interface for attachments
    """


class IEMailRepresentation(Interface):
    """Interface for
    """


class INotificationEmailSentEvent(IObjectEvent):
    """Event fired when a notification email is sent.
    """

    comment = Attribute('The comment entered by the user.')
    to_userids = Attribute('User ids of "to" recipients.')
    cc_userids = Attribute('User ids of "cc" recipients.')
