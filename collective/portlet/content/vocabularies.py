# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from collective.portlet.content import ContentPortletMessageFactory as _

class TitleDisplayVocabulary(object):
    """Vocabulary factory for title_display.
    """
    implements( IVocabularyFactory )
    
    def __call__(self, context):
        return SimpleVocabulary(
            [ SimpleTerm(value=pair[0], token=pair[0], title=pair[1]) for pair in [
                (u'hidden', _(u'Hidden')),
                 (u'text', _(u'Display as text')),
                 (u'link', _(u'Display as a link')),                                                         
            ]]
        )

TitleDisplayVocabularyFactory = TitleDisplayVocabulary()

class ItemDisplayVocabulary(object):
    """Vocabulary factory for item_display.
    """
    implements( IVocabularyFactory )
    
    def __call__(self, context):
        return SimpleVocabulary(
            [ SimpleTerm(value=pair[0], token=pair[0], title=pair[1]) for pair in [
                (u'date', _(u'Date')),
                (u'image', _(u'Image')),
                (u'description', _(u'Description')),
                (u'body', _(u'Body')),                                                        
            ]]
        )

ItemDisplayVocabularyFactory = ItemDisplayVocabulary()

