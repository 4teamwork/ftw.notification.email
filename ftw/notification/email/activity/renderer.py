from ftw.activity.browser.renderer import DefaultRenderer
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component.hooks import getSite


class NotificationRenderer(DefaultRenderer):
    index = ViewPageTemplateFile('templates/notification.pt')

    def position(self):
        return 900

    def match(self, activity, obj):
        return activity.attrs['action'] == 'notification:email_sent'

    def render(self, activity, obj):
        portal_transforms = getToolByName(self.context, 'portal_transforms')
        comment_html = portal_transforms.convertTo(
            'text/html',
            activity.attrs['notification:comment'],
            mimetype='text/-x-web-intelligent').getData()

        options = {
            'comment': comment_html,
            'to_names': self.userids_to_names(
                activity.attrs['notification:to_userids']),
            'cc_names': self.userids_to_names(
                activity.attrs['notification:cc_userids']),
        }
        return self.index(activity=activity, obj=obj, **options)

    def userids_to_names(self, userids):
        return u', '.join(map(self.get_fullname_of, userids))

    def get_fullname_of(self, userid):
        membership = getToolByName(getSite(), 'portal_membership')
        member = membership.getMemberById(userid)
        if not member:
            result = userid or 'N/A'
        else:
            result = member.getProperty('fullname') or userid

        if not isinstance(result, unicode):
            result = result.decode('utf-8')

        return result
