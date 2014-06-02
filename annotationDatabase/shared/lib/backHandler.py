""" annotationDatabase.shared.lib.backHandler

    This module makes it easy to implement Django pages which let the user
    "drill down" to a given page and then return back to the page they were on,
    where the page they were on could vary depending on context.  For example,
    if you use the Dango pagination system to display a list of records, and
    that list includes a link to view the details of a record, you can use the
    backHandler module to return the user back to their current position in the
    paginated list.

    Note that the URLs are deliberately obfuscated so the user can't read them.
"""
import base64

from django.http import HttpResponseRedirect

#############################################################################

def encode_url(url):
    """ Encode the given URL.

        We return the given URL, converted to an obfuscated string which can be
        safely used as an HTTP "GET" parameter.
    """
    return base64.urlsafe_b64encode(str(url))

#############################################################################

def decode_url(encoded_url):
    """ Decode a URL previously encoded using the encode_url() function.
    """
    return base64.urlsafe_b64decode(str(encoded_url))

#############################################################################

def encode_current_url(request):
    """ Encode and return the URL associated with the given HttpRequest object.

        We extract the URL associated with the given page and encode it using
        the encode_url() function, defined above.
    """
    url = request.get_full_path()
    return encode_url(url)

#############################################################################

def go_back_to(encoded_url):
    """ Return an HttpResponseRedirect redirecting to the given encoded URL.

        This function decodes the given URL and then returns an
        HttpResponseRedirect object redirecting the user back to that URL.
        Note that this function is provided for convenience.
    """
    url = decode_url(encoded_url)
    return HttpResponseRedirect(url)

#############################################################################

def get_back_param(request, param_name="back", default="/"):
    """ Extract the "back" parameter from the given HttpRequest.

        If we have a parameter with the given parameter name, we extract that
        parameter and decode it, returning the decoded URL.  Otherwise, we
        return the given default URL.
    """
    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        params = {} # Should never happen.

    if param_name in params:
        return decode_url(params[param_name])
    else:
        return default

