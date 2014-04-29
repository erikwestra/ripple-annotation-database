""" authentication.views.logout

    This module defines the "logout" view for the Authentication app.
"""
from ..       import auth_controller
from ..models import *

#############################################################################

def logout(request):
    """ Respond to the "logout" URL.

        We log the user out, and then redirect the user back to the login page.
    """
    session_token = request.session.get("authentication_session_token")
    if session_token == None:
        # No session -> redirect back to the "login" page.
        return auth_controller.redirect_to_login()

    try:
        session = Session.objects.get(session_token=session_token)
    except Session.DoesNotExist:
        # No session -> redirect back to the "login" page.
        return auth_controller.redirect_to_login()

    session.delete()
    del request.session['authentication_session_token']

    return auth_controller.redirect_to_login()

