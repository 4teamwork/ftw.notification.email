from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.notification.email.composer import HTMLComposer

_marker = object()


class BaseEmailRepresentation(object):
    """returns a email representation of an IBaseContent for HTML.
    """

    template = ViewPageTemplateFile('base.pt')
    #XXX: replace with CSSVIew
    stylesheet = """
    body {
        font-family: Arial !important;
        font-size: 10pt !important;
    }
    h1, h2, h3, h4, h5, h6 {
        border: none;
        font-family:  Arial !important;
    }
    div, p, ul, dl, ol {
        width: auto;
    }
    ul, ol, dl {
        padding-right: 0.5em;
    }
    ul {
        list-style-type: square;
    }
    .documentDescription {
        font-weight: bold;
    }
    pre {
        border: 1pt dotted black;
        white-space: pre;
        overflow: auto;
        padding: 1em 0;
    }
    table.listing,
    table.listing td {
        border: 1pt solid black;
        border-collapse: collapse;
    }
    a {
        color: Black !important;
        padding: 0 !important;
        text-decoration: underline !important;
    }
    a:link, a:visited {
        color: #520;
        background: transparent;
    }

    hr{
        border:none;
        border-bottom:1px solid grey;
    }
    """

    def __init__(self, context):
        self.context = aq_inner(context)
        self.request = self.context.REQUEST
        self.comment = None

    def __call__(self, subject, to_list, cc_list, message,
                 attachments=_marker, **kwargs):

        if attachments is _marker:
            attachments = []

        self.comment = message.replace('\n', '<br />')
        self.__dict__.update(kwargs)
        composer = HTMLComposer(self.template(self), subject, to_list, cc_list,
                                replyto_address=kwargs['sender'])
        return composer.render(filter_tags=False,
                               override_vars=dict(stylesheet=self.stylesheet),
                               attachments=attachments)
