from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from email import Encoders
from email import Utils
from email.Header import Header
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import formatdate
from ftw.notification.email.interfaces import IEMailComposer
from zope import component
from zope import interface
import Products.CMFPlone.interfaces
import StringIO
import formatter
import htmllib
import persistent
import stoneagehtml
import string
import zope.sendmail.mailer


_ = lambda x: x


def _render_cachekey(method, self, vars_):
    return (vars_)


_marker = object()


def create_html_mail(subject, html, text=None, from_addr=None, to_addr=None,
                     headers=None, encoding='UTF-8', attachments=_marker):
    """Create a mime-message that will render HTML in popular
    MUAs, text in better ones.
    """

    if attachments is _marker:
        attachments = []

    # Use DumbWriters word wrapping to ensure that no text line
    # is longer than plain_text_maxcols characters.
    plain_text_maxcols = 72
    html = html.encode(encoding)
    if text is None:
        # Produce an approximate textual rendering of the HTML string,
        # unless you have been given a better version as an argument
        textout = StringIO.StringIO()
        formtext = formatter.AbstractFormatter(formatter.DumbWriter(
                        textout, plain_text_maxcols))
        parser = htmllib.HTMLParser(formtext)
        parser.feed(html)
        parser.close()

        # append the anchorlist at the bottom of a message
        # to keep the message readable.
        counter = 0
        anchorlist = "\n\n" + ("-" * plain_text_maxcols) + "\n\n"
        for item in parser.anchorlist:
            counter += 1
            anchorlist += "[%d] %s\n" % (counter, item)

        text = textout.getvalue() + anchorlist
        del textout, formtext, parser, anchorlist
    else:
        text = text.encode(encoding)

    # if we would like to include images in future, there should
    # probably be 'related' instead of 'mixed'
    msg = MIMEMultipart('mixed')
    msg['Subject'] = Header(subject, encoding)
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Date'] = formatdate(localtime=True)
    msg["Message-ID"] = Utils.make_msgid()
    if headers:
        for key, value in headers.items():
            msg[key] = value

    msg.preamble = 'This is a multi-part message in MIME format.'

    alternatives = MIMEMultipart('alternative')
    msg.attach(alternatives)
    alternatives.attach(MIMEText(text, 'plain', _charset=encoding))
    alternatives.attach(MIMEText(html, 'html', _charset=encoding))

    #add the attachments
    for f, name, mimetype in attachments:
        if mimetype is None:
            mimetype = ('application', 'octet-stream')
        maintype, subtype = mimetype
        if maintype == 'text':
            # XXX: encoding?
            part = MIMEText(f.read(), _subtype=subtype)
        else:
            part = MIMEBase(maintype, subtype)
            part.set_payload(f.read())
            Encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition', 'attachment; filename="%s"' % name)
        msg.attach(part)
    return msg


class HTMLComposer(persistent.Persistent):
    # """
    #   >>> from zope.interface.verify import verifyClass
    #   >>> from collective.dancing.interfaces import IHTMLComposer
    #   >>> verifyClass(IHTMLComposer, HTMLComposer)
    #   True
    # """

    interface.implements(IEMailComposer)

    title = _(u'HTML E-Mail')

    def __init__(self, message, subject, to_addresses, cc_addresses=_marker,
        from_name=u'', from_address='', stylesheet='', replyto_address=''):

        if cc_addresses is _marker:
            cc_addresses = []

        properties = component.getUtility(
            Products.CMFCore.interfaces.IPropertiesTool)
        self.encoding = properties.site_properties.getProperty(
            'default_charset', 'utf-8')
        self.stylesheet = stylesheet
        self.from_name = from_name or properties.email_from_name
        self.from_address = from_address or properties.email_from_address
        self.to_addresses = to_addresses and to_addresses or None
        self.cc_addresses = cc_addresses
        self.replyto_address = replyto_address
        self.subject = subject
        self.message = message
        self.header_text = u""
        self.footer_text = u""

    template = ViewPageTemplateFile('templates/composer-html.pt')

    context = None

    @property
    def request(self):
        site = zope.component.hooks.getSite()
        return site.REQUEST

    def _prepare_address(self, name, mail, charset):
        if not isinstance(name, unicode):
            name = name.decode(charset)
        if not isinstance(mail, unicode):
            # mail has to be be ASCII!!
            mail = mail.decode(charset).encode('us-ascii', 'replace')
            #TODO : assert that mail is now valid. (could have '?' from repl.)
        return Utils.formataddr((str(Header(name, charset)), mail))

    @property
    def _from_address(self):
        return self._prepare_address(
            self.from_name, self.from_address, self.encoding)

    def _to_addresses(self, to_addresses):
        addresses = []
        for name, mail in to_addresses:
            addresses.append(self._prepare_address(name, mail, self.encoding))
        return ', '.join(addresses)

    @property
    def _replyto_address(self):
        name, mail = self.replyto_address
        return self._prepare_address(name, mail, self.encoding)

    @property
    def language(self):
        return self.request.get('LANGUAGE')

    def _vars(self):
        """Provide variables for the template.

        Override this or '_more_vars' in your custom HTMLComposer to
        pass different variables to the templates.
        """
        variables = {}
        site = component.getUtility(
            Products.CMFPlone.interfaces.IPloneSiteRoot)
        #site = utils.fix_request(site, 0)
        #lambda t: transform.URL(site).__call__(t, subscription)
        fix_urls = lambda t: t
        variables['site_url'] = site.absolute_url()
        variables['site_title'] = site.Title()
        variables['subject'] = self.subject
        variables['message'] = self.message
        # Why would header_text or footer_text ever be None?
        variables['header_text'] = fix_urls(self.header_text or u"")
        variables['footer_text'] = fix_urls(self.footer_text or u"")
        variables['stylesheet'] = self.stylesheet
        variables['from_addr'] = self._from_address
        variables['to_addr'] = self._to_addresses(self.to_addresses)
        headers = variables['more_headers'] = {}
        if self.replyto_address:
            headers['Reply-To'] = self._replyto_address
        cc_addr = self._to_addresses(self.cc_addresses)
        if cc_addr:
            headers['CC'] = cc_addr

        # It'd be nice if we could use an adapter here to override
        # variables.  We'd probably want to pass 'items' along to that
        # adapter.

        return variables

    #@volatile.cache(_render_cachekey)
    def _html(self, variables, **kwargs):
        html = self.template(**variables)
        return stoneagehtml.compactify(html, **kwargs).decode('utf-8')

    def html(self, override_vars=None, template_vars=_marker, **kwargs):
        if template_vars is _marker:
            template_vars = {}

        variables = self._vars()

        if override_vars is None:
            override_vars = {}
        variables.update(override_vars)

        html = self._html(variables, **kwargs)
        html = string.Template(html).safe_substitute(template_vars)
        return html

    def render(self, override_vars=None, template_vars=_marker,
               attachments=_marker, **kwargs):

        if template_vars is _marker:
            template_vars = {}

        if attachments is _marker:
            attachments = []

        variables = self._vars()

        if override_vars is None:
            override_vars = {}
        variables.update(override_vars)
        message = create_html_mail(
            variables['subject'],
            self.html(
                override_vars=override_vars,
                template_vars=template_vars,
                **kwargs),
            from_addr=variables['from_addr'],
            to_addr=variables['to_addr'],
            headers=variables.get('more_headers'),
            encoding=self.encoding,
            attachments=attachments)

        return message
