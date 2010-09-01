from zope.component import getMultiAdapter

from DateTime import DateTime
from zope.component import queryUtility
from ftw.notification.base.interfaces import INotifier
from ftw.notification.base import notification_base_factory as _


def notification_sent(event):
    obj = event.obj
    comment = event.comment
    notifier = queryUtility(INotifier, name='email-notifier')
    if notifier is None:
        return

    if event.action is None:
        action = _(u"label_send_notification", default=u"Send Notification")
    else:
        action = event.action

    if event.actor is None:
        portal_state = getMultiAdapter((obj, obj.REQUEST),
                                        name=u'plone_portal_state')
        actor = portal_state.member().getId()
    else:
        actor = event.actor

    if event.time is None:
        time = DateTime()
    else:
        time = event.time

    to_list = obj.REQUEST.get('to_list', [])
    kwargs = dict(action=action, actor=actor, time=time)
    notifier.send_notification(to_list=to_list, message=comment,
                               object_= obj, **kwargs)
