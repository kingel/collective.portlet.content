from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from DateTime import DateTime

from collective.portlet.content import contentportlet

from collective.portlet.content.tests.base import TestCase


class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def test_portlet_type_registered(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlet.content.ContentPortlet')
        self.assertEquals(portlet.addview,
                          'collective.portlet.content.ContentPortlet')

    def test_interfaces(self):
        # TODO: Pass any keyword arguments to the Assignment constructor
        portlet = contentportlet.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlet.content.ContentPortlet')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        # TODO: Pass a dictionary containing dummy form inputs from the add
        # form.
        # Note: if the portlet has a NullAddForm, simply call
        # addview() instead of the next line.
        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0],
                                   contentportlet.Assignment))

    def test_invoke_edit_view(self):
        # NOTE: This test can be removed if the portlet has no edit form
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = contentportlet.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, contentportlet.EditForm))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)

        # TODO: Pass any keyword arguments to the Assignment constructor
        assignment = contentportlet.Assignment()

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, contentportlet.Renderer))


class TestRenderer(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))
        
        self.content_tmpl = """<p><a href="%s">Home</a></p>"""
        
        # make a document with some realistic content
        self.portal.invokeFactory('Document', 'quick-links')
        self.portal['quick-links'].setTitle('Quick Links')
        self.portal['quick-links'].setText(
            self.content_tmpl % self.portal.portal_url())
        
        self.item_url_path = self.portal['quick-links'].virtual_url_path()
        self.portal_url_path = self.portal.virtual_url_path()
        
    def _setLanguage(self, language):
        request = self.app.REQUEST
        request['set_language'] = language
        self.portal.portal_languages.setLanguageBindings()
    
    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)
        
        assignment = assignment or contentportlet.Assignment()
        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer)
    
    def test_render_body(self):
        r = self.renderer(
            context=self.portal,
            assignment=contentportlet.Assignment(
                content=self.item_url_path[len(self.portal_url_path):],
                item_display=[u'body'],
            )
        )
        
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless(self.content_tmpl % self.portal.portal_url() in output)
    
    def test_i18n_render_body(self):
        # determine if we can test this
        try:
            from Products.LinguaPlone.tests.utils import makeTranslation
        except ImportError:
            # oh well, can't test this
            self.fail("Products.LinguaPlone needed for test_i18n_render_body.")
        
        # lingua plone setup
        self.portal.portal_languages.addSupportedLanguage('de')
        
        # now we make a translation
        self.portal['quick-links'].setLanguage('en')
        ql_german = makeTranslation(self.portal['quick-links'], 'de')
        ql_german.setTitle('Quick Links DE')
        ql_german.setText(self.content_tmpl % self.portal.portal_url() + "DE")
        
        #  set the language to German
        self._setLanguage('de')
        
        
        r = self.renderer(
            context=self.portal,
            assignment=contentportlet.Assignment(
                content=self.item_url_path[len(self.portal_url_path):],
                item_display=[u'body'],
            )
        )
        
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless(self.content_tmpl % self.portal.portal_url() + "DE" \
            in output)
            
    def test_render_options(self):
        ql = self.portal['quick-links']
        ql.setDescription(u'Quick links description')
        
        r = self.renderer(
            context=self.portal,
            assignment=contentportlet.Assignment(
                portlet_title=u'Quick Links Portlet',
                content=self.item_url_path[len(self.portal_url_path):],
                title_display=u'link',
                item_display=[u'date', u'description'],
                more_text = u'Read more',
            )
        )

        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless(u'Quick Links Portlet' in output)
        self.failUnless(ql.absolute_url() in output)
        self.failUnless(self.folder.toLocalizedTime(DateTime(), long_format=False) in output)
        self.failUnless(u'Quick links description' in output)
        self.failUnless('Read more' in output)

    def test_i18n_render_options(self):
        # determine if we can test this
        try:
            from Products.LinguaPlone.tests.utils import makeTranslation
        except ImportError:
            # oh well, can't test this
            self.fail("Products.LinguaPlone needed for test_i18n_render_options.")

        # lingua plone setup
        self.portal.portal_languages.addSupportedLanguage('de')

        # now we make a translation
        self.portal['quick-links'].setLanguage('en')
        ql_german = makeTranslation(self.portal['quick-links'], 'de')
        ql_german.setDescription('Quick links description DE')

        #  set the language to German
        self._setLanguage('de')


        r = self.renderer(
            context=self.portal,
            assignment=contentportlet.Assignment(
                portlet_title=u'Quick Links Portlet DE',
                content=self.item_url_path[len(self.portal_url_path):],
                title_display=u'link',
                item_display=[u'date', u'description'],
                more_text = u'Read more',
            )
        )

        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless(u'Quick Links Portlet DE' in output)
        self.failUnless(ql_german.absolute_url() in output)
        self.failUnless(self.folder.toLocalizedTime(DateTime(), long_format=False) in output)
        self.failUnless(u'Quick links description DE' in output)
        self.failUnless('Read more' in output)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
