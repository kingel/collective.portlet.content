from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from zope.schema.vocabulary import SimpleVocabulary
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.interfaces.Translatable import ITranslatable
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
        required=False,
    )

    content = schema.Choice(title=_(u"Content Item"),
        required=True,
        source=SearchableTextSourceBinder(
            {},
            default_query='path:'
        )
    )
                            
    title_display = schema.Choice(
        title=_(u'Item Title'),
        vocabulary=SimpleVocabulary.fromItems([
            (_(u'Hidden'), u'hidden'),
            (_(u'Display as text'), u'text'),
            (_(u'Display as a link'), u'link'),
        ]),
        default=u'link',
        required=True,
    )
    
    item_display = schema.List(
        title=_(u'Item Display'),
        value_type=schema.Choice(
            vocabulary=SimpleVocabulary.fromItems([
                (_(u'Date'), u'date'),
                (_(u'Image'), u'image'),
                (_(u'Description'), u'description'),
                (_(u'Body'), u'body'),
            ]),
        ),
        default=[u'image', u'description'],
        required=False,
    )
    
    more_text = schema.TextLine(
        title=_(u'Read More Link'),
        description=_(u'Enter the text for the read more link. \
            Leave blank to hide the read more link.'),
        default=u'Read more',
        required=False,
    )

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IContentPortlet)

    portlet_title = u''
    content = None
    title_display = u'link'
    item_display = [u'image', u'description']
    more_text = u'Read more'

    def __init__(self, portlet_title=u'', content=None, title_display=u'link', \
        item_display=[u'image', u'description'], more_text=u'Read more'):
        self.portlet_title = portlet_title
        self.content = content
        self.title_display = title_display
        self.item_display = item_display
        self.more_text = more_text

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return self.portlet_title or "Content Portlet"

class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    
    render = ViewPageTemplateFile('contentportlet.pt')
    
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
        """
        
        if not u'body' in self.data.item_display:
            return None

        if ITranslatable.isImplementedBy(self.content):
            return self.content.getText().decode(self.content.getCharset())
        return self.content.getText()
        
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
        
        tool = getToolByName(self.context, 'portal_languages', None)
        if tool is not None and ITranslatable.isImplementedBy(item):
            lang = tool.getLanguageBindings()[0]
            return item.getTranslation(lang)
        return item

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
