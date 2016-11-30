from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.configuration import xmlconfig


class NotificationIntegrationLayer(PloneSandboxLayer):
    """Layer for integration tests."""

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.notification.email:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])


NOTIFICATION_INTEGRATION_FIXTURE = NotificationIntegrationLayer()
NOTIFICATION_INTEGRATION_TESTING = IntegrationTesting(
    bases=(NOTIFICATION_INTEGRATION_FIXTURE, ),
    name="Notification:Integration")

NOTIFICATION_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(NOTIFICATION_INTEGRATION_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="Notification:Functional")
