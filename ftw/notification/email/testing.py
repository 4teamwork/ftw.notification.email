from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from zope.configuration import xmlconfig
from ftw.builder.testing import BUILDER_LAYER


class NotificationIntegrationLayer(PloneSandboxLayer):
    """Layer for integration tests."""

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        # Load testing zcml (optional)
        import ftw.notification.base
        xmlconfig.file('configure.zcml', ftw.notification.base,
                       context=configurationContext)

        import ftw.notification.email
        xmlconfig.file('configure.zcml', ftw.notification.email,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.notification.email:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])


NOTIFICATION_INTEGRATION_FIXTURE = NotificationIntegrationLayer()
NOTIFICATION_INTEGRATION_TESTING = IntegrationTesting(
    bases=(NOTIFICATION_INTEGRATION_FIXTURE, ),
    name="Notification:Integration")

NOTIFICATION_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(NOTIFICATION_INTEGRATION_FIXTURE,),
    name="Notification:Functional")
