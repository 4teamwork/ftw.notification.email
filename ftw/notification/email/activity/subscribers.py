from ftw.activity.catalog import get_activity_soup
from ftw.activity.catalog.record import ActivityRecord


def notification_email_sent_activity(
        obj, event, actor_userid=None, date=None,
        comment=None, to_userids=None, cc_userids=None):
    record = ActivityRecord(obj, 'notification:email_sent',
                            actor_userid=actor_userid, date=date)

    record.attrs['notification:comment'] = comment or event.comment
    record.attrs['notification:to_userids'] = tuple(
        to_userids or event.to_userids)
    record.attrs['notification:cc_userids'] = tuple(
        cc_userids or event.cc_userids)
    return get_activity_soup().add(record)
