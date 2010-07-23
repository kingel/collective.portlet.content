from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

try:
    from Products.LinguaPlone.interfaces import ITranslatable
    LINGUAPLONE_SUPPORT = True
except ImportError:
    # Linguaplone not installed
    LINGUAPLONE_SUPPORT = False

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from collective.portlet.content import ContentPortletMessageFactory as _


class IContentPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    content = schema.Choice(title=_(u"Target content object"),
                            description=_(u"Find the items to show"),
                            required=True,
                            source=SearchableTextSourceBinder({}, default_query='path:'))

    omit_border = schema.Bool(
        title=_(u"Omit portlet border"),
        description=_(u"Tick this box if you want to render the content item "
                      "selected above without the standard header, border "
                      "or footer."),
        required=True,
        default=False)

    omit_header = schema.Bool(
        title=_(u"Omit portlet header"),
        description=_(u"Tick this box if you want don't want the portlet "
                        "header to be displayed."),
        required=True,
        default=False)

    custom_header = schema.TextLine(
        title=_(u"Custom portlet header"),
        description=_(u"Set a custom header for the rendered portlet. Leave "
                       "empty to use the selected content's title."),
        required=False)

    footer = schema.TextLine(
        title=_(u"Portlet footer"),
        description=_(u"Text to be shown in the footer"),
        required=False)

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IContentPortlet)

    content = u""
    omit_border = False
    custom_header = u""
    footer = u""
    omit_header = False

    def __init__(self, content=None, omit_border=None, custom_header=None,
            footer=None, omit_header=None):
        self.content = content
        self.omit_border = omit_border
        self.custom_header = custom_header
        self.footer = footer
        self.omit_header = omit_header

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Content portlet"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('contentportlet.pt')

    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)
        self._setContentObject() 

    def _setContentObject(self):
        if not self.data.content:
            return None
        portalpath = getToolByName(self.context, 'portal_url').getPortalPath()
        ob = self.context.unrestrictedTraverse(str(portalpath + self.data.content))
        if LINGUAPLONE_SUPPORT:
            tool = getToolByName(self.context, 'portal_languages', None)
            if tool is not None and ITranslatable.providedBy(ob):
                lang = tool.getLanguageBindings()[0]
                ob = ob.getTranslation(lang) or ob

        self._ob = ob
    
    def text(self):
        return self._ob.getText().decode(self._ob.getCharset())

    def more_url(self):
       return self._ob.absolute_url()
    
    def has_footer(self):
       return bool(self.data.footer)

    def header(self):
        return self.data.custom_header or self._ob.Title()

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IContentPortlet)
    form_fields['content'].custom_widget = UberSelectionWidget

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IContentPortlet)
    form_fields['content'].custom_widget = UberSelectionWidget
