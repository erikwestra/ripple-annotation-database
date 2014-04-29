                               About the Box UI
                               ----------------

The "Box User Interface" is a way of displaying dialog boxes within a Django
web page.  BoxUI is implemented as a Django template which can be extended to
provide a user-interface consisting of a "dialog box" with the following
contents:

          +-------------------------------------+
          |+-----------------------------------+|
          ||               HEADER              ||
          |+-----------------------------------+|
          |+-----------------------------------+|
          ||                                   ||
          ||              CONTENTS             ||
          ||                                   ||
          |+-----------------------------------+|
          |+-----------------------------------+|
          ||               FOOTER              ||
          |+-----------------------------------+|
          +-------------------------------------+

The dialog box has a fixed width and height.  The header and footer also have
fixed heights, and the contents automatically takes up the remaining vertical
space.  The entire dialog box is centered within the web page, and uses a
standard colour scheme.


Using BoxUI
-----------

To use the BoxUI as the basis for an HTML template, make sure you add "boxUI"
to your list of INSTALLED_APPS, and then include the following at the top of
your template file:

  {% extends "boxUI/boxUI.html" %}
  {% load boxUI_tags %}

You then define the contents of your dialog box using the following template
blocks:

  config

    This template block is used to configure the dialog box.  You shouldn't put
    any real content into this block; instead, the block should be used to
    define various configuration settings for your dialog box, like this:

      {% block config %}
        {% set title = "My Page Title" %}
        {% set dialog_width = 500 %}
        {% set dialog_height = 300 %}
        {% set header_height = 50 %}
        {% set footer_height = 30 %}
      {% endblock %}

    'title' is the string to use for the page title, and the remaining values
    are the dimensions, in pixels, for the various parts of the dialog box.

  header

    The HTML code to appear in the dialog box's header.

  contents

    The HTML code to appear within the contents of the dialog box.

  footer

    The HTML code to appear within the footer of the dialog box.

  page_head

    An optional block of HTML code to insert into the page's < head > tag.

  dialog_prefix

    Optional HTML to insert before the start of the dialog box's < div > tag.

  dialog_suffix

    Optional HTML code to insert after the end of the dialog box's < div > tag.


CSS Styles
----------

The BoxUI provides the following CSS styles which you may find useful:

  white-text

    Makes text within an element white.  This works best for text placed within
    the dialog box, but not for input fields, etc.

  left

    Left-aligns the contents of a < div > element.

  right

    Right-aligns the contents of a < div > element.

  centre

    Centre-aligns the contents of a < div > element.

