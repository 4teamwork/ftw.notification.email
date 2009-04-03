class IFormatItem(interface.Interface):
    """A view that formats an item for use in a notification.

    Given an item as retrieved from a collector, this view returns a
    representation of the given item ready for inclusion in the
    message via the ``IComposer.render`` method.
    """

    def __call__():
        """Returns a unicode-string."""