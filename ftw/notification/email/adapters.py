from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from zope.component import hooks
from zope.i18n import translate


class BaseSubjectCreator(object):
    """An Overwritable Adapter to get the Subject"""

    def __init__(self, context):

        self.context = aq_inner(context)
        self.request = self.context.REQUEST

    def __call__(self, object_):
        site = hooks.getSite()
        site_title = site.Title()
        if isinstance(site_title, unicode):
            site_title = site_title.encode('utf-8')
        portal_properties = getToolByName(object_, 'portal_properties')
        default_subject = '[%s] %s: %s' % (
            site_title,
            translate(u'Notification',
                     domain="ftw.notification.email",
                     context=object_.REQUEST).encode('utf8'),
            object_.Title())
        subject = None
        try:
            sheet = portal_properties.ftw_notification_properties
        except AttributeError:
            subject = default_subject
        else:
            subject = sheet.getProperty(
                'notification_email_subject',
                default_subject) + ': ' + object_.Title()
        return subject


class AttachmentCreator(object):
    """An base-adapter to add attachments"""

    def __init__(self, context):
        self.context = aq_inner(context)
        self.request = self.context.REQUEST

    def __call__(self, object_):
        """Usualy this Adapters does nothing,
        bewlow is an example how implement an attachment using StringIO.

        @return tuple(file, name, mimetype)"""

        # mime_type = "text/calendar"
        # attachments = []
        # self.meeting_types = ['dates_additional',
        #                       'meeting_dates_additional',]

        # if object_.getMeeting_type() in self.meeting_types:
        #     ical_view = getattr(object_.aq_explicit, 'ics_view', None)
        #     if ical_view:
        #         ical_view = ical_view(
        #             object_.REQUEST, object_.REQUEST.RESPONSE)
        #         ical_file = StringIO(ical_view)
        #         ical_attachment = (
        #             ical_file, 'ICal.ics', mime_type.split('/'))
        #         attachments = [ical_attachment,]
        # return attachments
        return []
