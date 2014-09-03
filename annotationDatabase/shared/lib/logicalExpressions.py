""" logicalExpressions.py

    This module implements a generic mechanism for representing logical
    expressions, and converting these into Django database queries.

    A logical expression is a way of representing a search query.  It consists
    of one or more "simple expressions", which are strings of the form:

        <variable> <comparison> <value>

    For example, "name = 'john'" or "age < 20". These simple expressions can
    then be combined into more complex expressions using parentheses and "and",
    "or" or "not" operators.  For example:

        (name='john') and (age<20)
        not (name='john')

    The following comparisons are supported:

        =
        <
        >
        <=
        >=
        !=

    We provide a function for parsing a string into a LogicalExpression object.
    The LogicalExpression object can then be converted back to a string for
    display, or it can be used to build a Django database query.  You can also
    retrieve a list of the variables used in a LogicalExpression object.
"""
from django.db.models import Q

import pyparsing as pp

#############################################################################

def parse(s):
    """ Attempt to parse the given string as a logical expression.

        's' should be a string holding a logical expression.  We attempt to
        parse that string into a LogicalExpression object.

        Upon completion, we return a LogicalExpression object representing the
        parsed logical expression, or None if the expression could not be
        parsed.
    """
    variable = pp.Word(pp.alphas+"_", pp.alphanums+"_")

    comparison_op = (pp.Literal('<=') | pp.Literal('<') |
                     pp.Literal('>=') | pp.Literal('>') |
                     pp.Literal('!=') | pp.Literal('='))

    value = pp.quotedString

    term = pp.Group(variable + comparison_op + value)
    term.setParseAction(make_simple_expression)

    op_not = pp.CaselessLiteral("NOT")
    op_and = pp.CaselessLiteral("AND")
    op_or  = pp.CaselessLiteral("OR")

    expression = pp.infixNotation(term,
                                  [(op_not, 1, pp.opAssoc.RIGHT,
                                               make_negation_expression),
                                   (op_and, 2, pp.opAssoc.LEFT,
                                               make_complex_expression),
                                   (op_or,  2, pp.opAssoc.LEFT,
                                               make_complex_expression)])

    try:
        results = expression.parseString(s, parseAll=True)
    except pp.ParseException:
        return None
    return results.asList()[0]

#############################################################################
#                                                                           #
#                   I N T E R N A L   D E F I N I T I O N S                 #
#                                                                           #
#############################################################################

def make_simple_expression(s, loc, tokens):
    """ This parse action is used to build a SimpleExpression object.
    """
    variable   = tokens[0][0]
    comparison = tokens[0][1]
    value      = tokens[0][2][1:-1]
    return SimpleExpression(variable, comparison, value)

#############################################################################

def make_complex_expression(s, loc, tokens):
    """ This parse action is used to build a ComplexExpression object.
    """
    left_expr  = tokens[0][0]
    operator   = tokens[0][1]
    right_expr = tokens[0][2]
    return ComplexExpression(left_expr, operator, right_expr)

#############################################################################

def make_negation_expression(s, loc, tokens):
    """ This parse action is used to build a NegationExpression object.
    """
    expr = tokens[0][1]
    return NegationExpression(expr)

#############################################################################

class LogicalExpression(object):
    """ The base class for all expression objects.

        We define the shared behaviour implemented by our various sub-classes.
        Note that this is an abstract class, and should not be instantiated
        directly.
    """
    def to_string(self):
        """ Convert the LogicalExpression back into a string.
        """
        raise RuntimeError("Must be overridden")


    def to_django_query(self, converter=None):
        """ Convert the LogicalExpression into a Django search query.

            The parameters are as follows:

                'converter'

                    This can be used to change the way simple expressions are
                    converted into Django queries.  By default, a simple
                    expression is converted into a django.db.models.Q object
                    that compares the given field in the object against the
                    supplied value.  For more complex conversions, a converter
                    function can be supplied.

                    If 'converter' is not None, it should be a callable object
                    which looks like this:

                        myConverter(variable, comparison, value)

                    where the parameters are as follows:

                        'variable'

                            A string holding the desired variable to compare
                            against.
                            
                        'comparison'

                            A string indicating how to compare the variable
                            against the value.  This willl be one of the
                            following:

                                "="
                                "<"
                                ">"
                                "<="
                                ">="
                                "!="

                        'value'

                            The value to compare the variable against, as a
                            string.

                    Upon completion, your converter function should return a
                    django.db.models.Q object representing the query to be made
                    against the database to filter for this simple expression.

            Upon completion, we return a django.db.models.Q object which can be
            used to filter search results.
        """
        raise RuntimeError("Must be overridden")


    def get_variables(self):
        """ Return a list of the variables in this logical expression.
        """
        raise RuntimeError("Must be overridden")

    # =========================
    # == CONVENIENCE METHODS ==
    # =========================

    def __repr__(self):
        return "LogicalExpression(" + self.to_string() + ")"

    def __str__(self):
        return self.to_string()

#############################################################################

class SimpleExpression(LogicalExpression):
    """ Our internal representation of a simple expression.

        A simple expression represents a search of the form:

            <variable> <comparison> <value>
    """
    def __init__(self, variable, comparison, value):
        """ Standard initialiser.
        """
        if comparison not in ["=", "<", ">", "<=", ">=", "!="]:
            raise RuntimeError("Unsupported comparison: " + comparison)

        self._variable   = variable
        self._comparison = comparison
        self._value      = value


    def to_string(self):
        """ Implement LogicalExpression.to_string().
        """
        return "%s %s '%s'" % (self._variable, self._comparison, self._value)


    def to_django_query(self, converter=None):
        """ Implement LogicalExpression.to_django_query().
        """
        if converter != None:
            return converter(self._variable, self._comparison, self._value)
        else:
            # Use the default expression converter.  This looks for a field
            # with the variable name, and compares it against the supplied
            # value directly.
            if self._comparison == "=":
                args   = {self._variable + "__iexact" : self._value}
                negate = False
            elif self._comparison == "<":
                args   = {self._variable + "__lt" : self._value}
                negate = False
            elif self._comparison == ">":
                args   = {self._variable + "__gt" : self._value}
                negate = False
            elif self._comparison == "<=":
                args   = {self._variable + "__lte" : self._value}
                negate = False
            elif self._comparison == ">=":
                args   = {self._variable + "__gte" : self._value}
                negate = False
            elif self._comparison == "!=":
                args   = {self._variable : self._value}
                negate = True

            result = Q(**args)
            if negate:
                result = ~result

            return result


    def get_variables(self):
        """ Implement LogicalExpression.get_variables().
        """
        return [self._variable]

#############################################################################

class ComplexExpression(LogicalExpression):
    """ Our internal representation of a complex expression.

        A complex expression consists of a search of the form:

            <logical_expression> <logical_operator> <logical_expression>

        where <logical_operator> can be one of the following:

            and
            or

        Note that each <logical_expression> can be either a SimpleExpression or
        a ComplexExpression object.  Thus, ComplexExpression objects can be
        used recursively to represent nested parentheses.
    """
    def __init__(self, left_expression, logical_operator, right_expression):
        """ Standard initialiser.
        """
        if logical_operator.lower() not in ["and", "or"]:
            raise RuntimeError("Unsupported logical operator: " +
                               logical_operator)

        self._left_expression  = left_expression
        self._logical_operator = logical_operator.lower()
        self._right_expression = right_expression


    def to_string(self):
        """ Implement LogicalExpression.to_string().
        """
        return "(%s) %s (%s)" % (self._left_expression.to_string(),
                                 self._logical_operator.lower(),
                                 self._right_expression.to_string())


    def to_django_query(self, converter=None):
        """ Implement LogicalExpression.to_django_query().
        """
        left_filter  = self._left_expression.to_django_query(converter)
        right_filter = self._right_expression.to_django_query(converter)

        if self._logical_operator == "and":
            return left_filter & right_filter
        elif self._logical_operator == "or":
            return left_filter | right_filter


    def get_variables(self):
        """ Implement LogicalExpression.get_variables().
        """
        variables = []
        variables.extend(self._left_expression.get_variables())
        variables.extend(self._right_expression.get_variables())
        return variables

#############################################################################

class NegationExpression(LogicalExpression):
    """ Our internal representation of a negation expression.

        A negation expression consists of a search of the form:

            NOT <logical_expression>
    """
    def __init__(self, expression):
        """ Standard initialiser.
        """
        self._expression = expression


    def to_string(self):
        """ Implement LogicalExpression.to_string().
        """
        return "not (%s)" % self._expression.to_string()


    def to_django_query(self, converter=None):
        """ Implement LogicalExpression.to_django_query().
        """
        filter = self._expression.to_django_query(converter)
        return ~filter


    def get_variables(self):
        """ Implement LogicalExpression.get_variables().
        """
        return self._expression.get_variables()

