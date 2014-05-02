""" annotationDatabase.api.helpers

    This module implements various helper functions for the Annotation
    Database's "api" application.
"""
import sys
import uuid

from annotationDatabase.shared.models import *

#############################################################################

def auth_token_valid(auth_token):
    """ Return True if and only if the given authentication token is valid.
    """
    return Client.objects.filter(auth_token=auth_token).exists()

#############################################################################

def get_auth_token_for_testing():
    """ Create and return an authentication token, for testing.

        Note that this adds a dummy Client record, so it should only be used in
        unit tests.  For security, we raise a RuntimeError if this is called
        outside of the unit tests.
    """
    if "test" not in sys.argv:
        raise RuntimeError("get_auth_token_for_testing() called outside of " +
                           "unit tests!")

    random_string = uuid.uuid4().hex

    client = Client()
    client.name       = random_string
    client.auth_token = random_string
    client.save()

    return random_string

