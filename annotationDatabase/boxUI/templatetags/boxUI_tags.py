""" boxUI.templatetags.boxUI_tags

    This module defines the custom template tags used by the BoxUI template.
"""
from django import template

#############################################################################

# Define the module-level template.Libary object to use for registering
# template tags and filters.

register = template.Library()

#############################################################################

global_vars = {} # Maps variable name to value.

#############################################################################

class SetNode(template.Node):
    """ A custom template node for implementing the "set" template tag.
    """
    def __init__(self, variable, value):
        """ Standard initialiser.
        """
        self.variable = variable
        self.value    = value


    def render(self, context):
        """ Render the "set" template tag.

            We don't actually return anthing.  Instead, we store the given
            value into the given variable.
        """
        if self.value.startswith('"') and self.value.endswith('"'):
            value = self.value[1:-1]
        elif self.value.startswith("'") and self.value.endswith("'"):
            value = self.value[1:-1]
        else:
            value = self.value
        global_vars[self.variable] = value
        return ""

#############################################################################

def set_parser(parser, token):
    """ The parser function for the "set" template tag.
    """
    contents = token.split_contents()

    err_msg = "'%s' tag must be of the form: {%% %s <variable> = <value> %%}" \
            % (contents[0], contents[0])

    if len(contents) != 4: raise template.TemplateSyntaxError(err_msg)
    if contents[2] != "=": raise template.TemplateSyntaxError(err_msg)

    return SetNode(contents[1], contents[3])

#############################################################################

class GetNode(template.Node):
    """ A custom template node for implementing the "get" template tag.
    """
    def __init__(self, variable):
        """ Standard initialiser.
        """
        self.variable = variable


    def render(self, context):
        """ Render the "set" template tag.

            We return the value of the given variable.
        """
        return global_vars.get(self.variable, "")

#############################################################################

def get_parser(parser, token):
    """ The parser function for the "get" template tag.
    """
    contents = token.split_contents()

    err_msg = "'%s' tag must be of the form: {%% %s <variable> %%}" \
            % (contents[0], contents[0])

    if len(contents) != 2: raise template.TemplateSyntaxError(err_msg)

    return GetNode(contents[1])

#############################################################################

class GetHalfNode(template.Node):
    """ A custom template node for implementing the "get_half" template tag.
    """
    def __init__(self, variable):
        """ Standard initialiser.
        """
        self.variable = variable


    def render(self, context):
        """ Render the "set" template tag.

            We return the value of the given variable, divided by 2.
        """
        value = global_vars.get(self.variable)
        if value == None:
            return "0"
        else:
            try:
                value = float(value)
            except ValueError:
                return "0"
            return int(value/2)

#############################################################################

def get_half_parser(parser, token):
    """ The parser function for the "get_half" template tag.
    """
    contents = token.split_contents()

    err_msg = "'%s' tag must be of the form: {%% %s <variable> %%}" \
            % (contents[0], contents[0])

    if len(contents) != 2: raise template.TemplateSyntaxError(err_msg)

    return GetHalfNode(contents[1])

#############################################################################

# Register our custom template tags.

register.tag('set',      set_parser)
register.tag('get',      get_parser)
register.tag('get_half', get_half_parser)

