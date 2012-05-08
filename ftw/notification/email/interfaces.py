# pylint: disable=E0211, E0213
# E0211: Method has no argument
# E0213: Method should have "self" as first argument

from zope.interface import Interface
from ftw.notification.base.interfaces import INotifier


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
