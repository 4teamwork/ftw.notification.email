from zope import component
from zope import interface

class CMFDublinCoreHTMLFormatter(object):
    """Render a brief representation of an IBaseContent for HTML.
    """
    interface.implements(ftw.notification.email.interfaces.IFormatItem)
    component.adapts(Products.CMFCore.interfaces.IMinimalDublinCore,
                     zope.publisher.interfaces.browser.IBrowserRequest)

    template = """\
    <div>
      <h2><a href="%(url)s">%(title)s</a></h2>
      <p>%(description)s</p>
    </div>
    """
    
    def __init__(self, item, request):
        self.item = item
        self.request = request

    def __call__(self):
        i = self.item
        return self.template % dict(
            url=i.absolute_url(), title=i.Title(), description=i.Description())