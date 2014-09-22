""" annotationDatabase.shared.lib.booleans

    This module implements the concept of a "boolean" annotation value.  The
    annotation templates support "choice" annotations where the user can choose
    between one of several values.  This module provides helper functions that
    can be used to treat "choice" annotations as representings boolean
    (True/False) choices if the annotation template has one of several
    predefined values.

    The following choice values are considered to represent boolean choices:

        Yes/No
        Y/N
        True/False
        1/0

    Note that the choices can be in any order, and the choice value is
    case-insensitive.
"""
#############################################################################

def is_boolean(template_entry):
    """ Return True if this annotation template entry accepts a boolean value.

        'template_entry' is a Python dictionary containing the details for a
        single annotation template entry, as returned by a previous call to
        functions.get_template().  We return True if this type of annotation
        has a type of "choice", and choices which represent a boolean (yes/no)
        style value.
    """
    true_value,false_value = _template_to_true_false(template_entry)
    if true_value != None and false_value != None:
        return True
    else:
        return False

#############################################################################

def get_true_choice(template_entry):
    """ Return the "True" value for a boolean annotation template entry.

        Given an annotation template entry that was identified by the
        is_boolean() function, above, as being a boolean choice annotation, we
        return the value to use for a "true" choice.

        If this is not a boolean template entry, we return None.
    """
    true_value,false_value = _template_to_true_false(template_entry)
    return true_value

#############################################################################

def get_false_choice(template_entry):
    """ Return the "False" value for a boolean annotation template entry.

        Given an annotation template entry that was identified by the
        is_boolean() function, above, as being a boolean choice annotation, we
        return the value to use for a "false" choice.
    """
    true_value,false_value = _template_to_true_false(template_entry)
    return false_value

#############################################################################
#                                                                           #
#                    P R I V A T E   D E F I N I T I O N S                  #
#                                                                           #
#############################################################################

def _template_to_true_false(template_entry):
    """ Convert a template entry into a (true_value, false_value) tuple.

        'template_entry' is an annotation template entry, as passed to one of
        our public functions.  We return the corresponding true and false
        value, as defined by the template.  If this template entry does not
        represent a boolean choice, we return (None, None).
    """
    if template_entry['type'] != "choice": return (None, None)

    lower_choices = set()
    capitalized_choice = {}
    for choice in template_entry['choices']:
        lower_choices.add(choice[0].lower())
        capitalized_choice[choice[0].lower()] = choice[0]

    for true_lower,false_lower in [("yes",  "no"),
                                   ("y",    "n"),
                                   ("true", "false"),
                                   ("1",    "0")]:
        if lower_choices == set([true_lower, false_lower]):
            return (capitalized_choice[true_lower],
                    capitalized_choice[false_lower])

    return (None, None) # Not a boolean choice.

