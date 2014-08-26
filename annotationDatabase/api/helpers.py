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

#############################################################################

def set_current_annotation(account, key, value):
    """ Create or update the CurrentAnnotation for the given account and key.

        The parameters are as follows:

            'account'

                The address for the desired account, as a string.

            'key'

                The desired annotation key, as a string.

            'value'

                The current value of this annotation for this account, as a
                string.

        This should be called whenever a current annotation value is changed.
        We look to see if there is a CurrentAnnotation record for this account
        and key, and if so update it to the new value.  Otherwise, we create a
        CurrentAnnotation record for this account and key combination.
    """
    try:
        annotation_account = Account.objects.get(address=account)
    except Account.DoesNotExist:
        annotation_account = Account()
        annotation_account.address = account
        annotation_account.save()

    try:
        annotation_key = AnnotationKey.objects.get(key__iexact=key)
    except AnnotationKey.DoesNotExist:
        annotation_key = AnnotationKey()
        annotation_key.key = key
        annotation_key.save()

    try:
        annotation_value = AnnotationValue.objects.get(value__iexact=value)
    except AnnotationValue.DoesNotExist:
        annotation_value = AnnotationValue()
        annotation_value.value = value
        annotation_value.save()

    try:
        annotation = CurrentAnnotation.objects.get(account=annotation_account,
                                                   key=annotation_key)
    except CurrentAnnotation.DoesNotExist:
        annotation = CurrentAnnotation()
        annotation.account = annotation_account
        annotation.key     = annotation_key

    annotation.value = annotation_value
    annotation.save()

