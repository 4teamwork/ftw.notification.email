from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from zope.configuration import xmlconfig


class NotificationIntegrationLayer(PloneSandboxLayer):
    """Layer for integration tests."""

    defaultBases = (PLONE_FIXTURE,)

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


NOTIFICATION_INTEGRATION_FIXTURE = NotificationIntegrationLayer()
NOTIFICATION_INTEGRATION_TESTING = IntegrationTesting(
    bases=(NOTIFICATION_INTEGRATION_FIXTURE, ),
    name="Notification:Integration")

NOTIFICATION_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(NOTIFICATION_INTEGRATION_FIXTURE,),
    name="Notification:Functional")
