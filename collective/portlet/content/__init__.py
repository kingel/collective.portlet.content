# -*- coding: utf-8 -*-

from zope.i18nmessageid import MessageFactory
ContentPortletMessageFactory = MessageFactory('collective.portlet.content')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
