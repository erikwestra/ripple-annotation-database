""" middleware.cors.py

    This middleware component enables CORS (Cross-Origin Resource Sharing) for
    incoming requests.

    For information on the CORS standard, please refer to:

        http://enable-cors.org
"""
from django.http import HttpResponse

#############################################################################

class CORSMiddleware(object):
    """ Middleware component to enable CORS support for all incoming requests.

        This class is derived from:

            https://github.com/elevenbasetwo/django-cors.
    """
    def process_request(self, request):
        """ Respond to an incoming HTTP request.

            We return a blank response to an OPTIONS request, as defined by the
            CORS standard to "preflight" the request.
        """
        if request.method == 'OPTIONS':
            return HttpResponse()


    def process_response(self, request, response):
        """ Add the CORS headers to our HTTP response.
        """
        origin = request.META.get('HTTP_ORIGIN')
        if origin:
            response['Access-Control-Allow-Origin']  = origin
            response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

