Introduction
============

This portlet shows a content item as content in the portlet. 
It's LinguaPlone aware, and is initially created to provide a 
language-dependent address footer.

Author: Lennart Regebro <regebro@gmail.com>

Development funded by the Nordic Council and Nordic Concil of Ministers.
http://www.norden.org/


Compatibility
=============

The product is compatible with Plone 3 and Plone 4.

Tested on Plone 3.3.5 and Plone 4.0b5.


Installing
==========

Add `collective.portlet.content` to your buildout and re-run buildout.
Install the product in your Plone site using the Plone Control Panel
(`prefs_install_products_form`) or the ZMI's `portal_quickinstaller`.


Using
=====

Go to `@@manage-portlets`. If the product was installed properly, you'll have 
the option to add a Content Portlet.

Next, select a content item to display. It can be any type of item. You can
select which of the item's fields you want to display in the portlet's content
area:

* Title (either as a link to the content item or as plain text)
* Description
* Date
* Body text
* Image

When the content item doesn't have a selected field, it should work without
errors, but you'd obviously not see the field in the portlet.

You can set these options separately:

* portlet's title as shown in `@@manage-portlets` screen
* portlet header title as rendered on page 
  (use content's title or select custom)
* hide portlet header altogether
* conditionally show a portlet footer with a link to the content item 
  (link text is configurable)
* disable the portlet border

