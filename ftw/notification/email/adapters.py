from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from zope.app.component import hooks


class BaseSubjectCreator(object):
    """An Overwritable Adapter to get the Subject"""

    def __init__(self, context):

        self.context = aq_inner(context)
        self.request = self.context.REQUEST

    def __call__(self, object_):
        site = hooks.getSite()
        translationservice = getToolByName(object_, 'translation_service')
        portal_properties = getToolByName(object_, 'portal_properties')
        default_subject = '[%s] %s: %s' % (
            site.Title(),
            translationservice.translate(
                u'Notification',
                domain="ftw.notification.email",
                context=object_.REQUEST).encode('utf8'),
            object_.Title())
        subject = None
        try:
            sheet = portal_properties.ftw_notification_properties
        except AttributeError:
            subject = default_subject
        else:
            subject = sheet.getProperty('notification_email_subject', default_subject)+': '+object_.Title()
        return subject

