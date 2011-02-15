from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.app.component.hooks import getSite

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
from plone.app.controlpanel.widgets import MultiCheckBoxVocabularyWidget
from plone.memoize import instance

from collective.portlet.content import ContentPortletMessageFactory as _

class IContentPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    
    portlet_title = schema.TextLine(
        title=_(u'Portlet Title'),
        description=_('help_portlet_title',
                      default=u'Enter a title for this portlet. '
                               "This property is used as the portlet's title in "
                               'the "@@manage-portlets" screen. '
                               'Leave blank for "Content portlet".'),
        required=False,
    )

    custom_header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_('help_custom_header',
                      default=u"Set a custom header (title) for the rendered portlet. "
                               "Leave empty to use the selected content's title."),
        required=False,
    )

    title_display = schema.Choice(
        title=_(u'Item Title in portlet content'),
        description = _('help_title_display',
                        default=u"Do you want to render the item's title inside the "
                                 "portlet content, and if yes, how?\n"
                                 "Note that by default, the item's title will be "
                                 "displayed in the portlet header."),
        vocabulary='collective.portlet.content.title_display_vocabulary',
        default=u'hidden',
        required=True,
    )
    content = schema.Choice(title=_(u"Content Item"),
        required=True,
        source=SearchableTextSourceBinder(
            {},
            default_query='path:'
        )
    )
                            
   
    item_display = schema.List(
        title=_(u'Item Display'),
        description = _('help_item_display',
                        default=u"Select which of the selected item's fields will "
                                "be displayed in the portlet's content area. "
                                "Note that selecting Body (text) will not work for "
                                "an Image."),
        value_type=schema.Choice(
            vocabulary='collective.portlet.content.item_display_vocabulary',
        ),
        default=[u'date', u'image', u'description', u'body'],
        required=False,
    )
    
    more_text = schema.TextLine(
        title=_(u'Read More Link'),
        description=_('help_more_text',
                      default=u"Enter the text for the link in the portlet footer. "
                               "Leave blank for no footer."),
        default=u'',
        required=False,
    )

    omit_border = schema.Bool(
        title=_(u"Omit portlet border"),
        description=_('help_omit_border',
                      default=u"Tick this box if you want to render the content item "
                               "selected above without the standard header, border "
                               "or footer."),
        required=True,
        default=False)

    omit_header = schema.Bool(
        title=_(u"Omit portlet header"),
        description=_('help_omit_header',
                      default=u"Tick this box if you don't want the portlet "
                               "header to be displayed."),
        required=True,
        default=False)

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IContentPortlet)

    portlet_title = u''
    content = None
    title_display = u'hidden'
    item_display = [u'image', u'description']
    more_text = u''
    omit_border = False
    custom_header = u""
    omit_header = False

    def __init__(self, portlet_title=u'', content=None, title_display=u'link', 
            item_display=[u'image', u'description'], more_text=u'',
            omit_border=None, custom_header=None, omit_header=None):
        self.portlet_title = portlet_title
        self.content = content
        self.omit_border = omit_border
        self.custom_header = custom_header
        self.omit_header = omit_header
        self.title_display = title_display
        self.item_display = item_display
        self.more_text = more_text

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        msg = _(u"Content portlet")
        return self.portlet_title or msg

class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('contentportlet.pt')

    @instance.memoizedproperty
    def content(self):
        """
        Returns the content object or None if it does not exist.
        """

        if not self.data.content:
            return None

        portal_path = getToolByName(self.context, 'portal_url').getPortalPath()
        item = self.context.restrictedTraverse(
            str(portal_path + self.data.content),
            None
        )

        if LINGUAPLONE_SUPPORT:
            tool = getToolByName(self.context, 'portal_languages', None)
            if tool is not None and ITranslatable.providedBy(item):
                lang = tool.getLanguageBindings()[0]
                item = item.getTranslation(lang) or item

        return item
    
    def date(self):
        """
        Returns the item date or None if it should not be displayed.
        """
        
        if not u'date' in self.data.item_display:
            return None
            
        return self.content.Date()
    
    def image(self):
        """
        Returns the item image or None if it should not be displayed.
        """
        
        if not u'image' in self.data.item_display:
            return None
            
        return self.content.restrictedTraverse('image_thumb', None)
        
    def description(self):
        """
        Returns the item description or None if it should not be displayed.
        """

        if not u'description' in self.data.item_display:
            return None

        return self.content.Description()
    
    def body(self):
        """
        Returns the body HTML or None if it should not be displayed.
        (or is not present on the object)
        """
        
        if not u'body' in self.data.item_display:
            return None

        # Currently nothing stops you from trying to get text from an Image
        if hasattr(self.content, 'getText'):
            text = self.content.getText()
        else:
            text = None

        return text
        
    
    def more_url(self):
       return self.content.absolute_url()
    
    def header(self):
        return self.data.custom_header or self.content.Title()

    def has_footer(self):
       return bool(self.data.more_text)


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IContentPortlet)
    form_fields['content'].custom_widget = UberSelectionWidget
    form_fields['item_display'].custom_widget = MultiCheckBoxVocabularyWidget

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IContentPortlet)
    form_fields['content'].custom_widget = UberSelectionWidget
    form_fields['item_display'].custom_widget = MultiCheckBoxVocabularyWidget
