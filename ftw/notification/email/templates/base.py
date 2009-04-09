from zope import component
from zope import interface
from Acquisition import aq_parent, aq_base, aq_inner
from ftw.sendmail.composer import HTMLComposer
from zope.app.pagetemplate import ViewPageTemplateFile

class BaseEmailRepresentation(object):
    """returns a email representation of an IBaseContent for HTML.
    """
    
    template = ViewPageTemplateFile('base.pt')
    
    def __init__(self, context):
         self.context = aq_inner(context)
         self.request = self.context.REQUEST

    def __call__(self, subject, to_list, message, **kwargs):
        self.comment = message.replace('\n', '<br />')
        self.__dict__.update(kwargs)
        composer = HTMLComposer(self.template(self), subject, to_list)
        return composer.render()