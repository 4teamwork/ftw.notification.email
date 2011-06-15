from Products.PloneTestCase import ptc
from ftw.notification.email.testing import ftw_notification_layer


class FtwNotificationTestCase(ptc.PloneTestCase):
    """Base class for integration tests."""

    layer = ftw_notification_layer
