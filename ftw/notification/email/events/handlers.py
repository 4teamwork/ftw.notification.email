from DateTime import DateTime
from ftw.journal.events.events import JournalEntryEvent
from ftw.notification.base import notification_base_factory as _
from ftw.notification.base.interfaces import INotifier
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.event import notify
from zope.i18n import translate


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
    cc_list = obj.REQUEST.get('cc_list', [])

    journal_comment = translate(
        msgid=u'journal_notification_text',
        domain='ftw.notification.email',
        context=obj.REQUEST,
        mapping=dict(
            to_list=len(to_list) > 0 and ', '.join(to_list) + '\n' or '-',
            cc_list=len(cc_list) > 0 and ', '.join(cc_list) + '\n' or '-',
            comment=comment))

    notify(JournalEntryEvent(obj, journal_comment, action))

    kwargs = dict(action=action, actor=actor, time=time)
    notifier.send_notification(
        to_list=to_list,
        cc_list=cc_list,
        message=comment,
        object_=obj,
        **kwargs)
