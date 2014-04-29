""" authentication.auth_controller

    This module allows the Django project to interact with the Authentication
    app.  It provides helper functions to do things like check if a user is
    logged in, and to redirect the user to the appropriate login page.
"""
import datetime

from django.http              import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils             import timezone

import app_settings
from models import *

#############################################################################

def is_logged_in(request):
    """ Return True if the user is currently logged in.

        'request' should be the HttpRequest object passed to your view
        function.
    """
    session = _get_session(request)
    if session == None:
        return False
    else:
        return True

#############################################################################

def is_admin(request):
    """ Return True if the user is logged in as an administrator.

        'request' should be the HttpRequest object passed to your view
        function.
    """
    session = _get_session(request)
    if session == None:
        return False

    if session.user.type == app_settings.ADMIN_USER_TYPE:
        return True
    else:
        return False

#############################################################################

def get_username(request):
    """ Return the username for the currently logged-in user.

        'request' should be the HttpRequest object passed to your view
        function.
        
        We return the unique username for the currently logged-in user, or None
        if the user is not currently logged in.
    """
    session = _get_session(request)
    if session == None:
        return None
    else:
        return session.user.username

#############################################################################

def get_user_type(request):
    """ Return the "type" for the currently logged-in user.

        'request' should be the HttpRequest object passed to your view
        function.

        We return a string containing the type for the currently logged-in
        user, or None if the user is not currently logged in.

        Note that the user type will be one of the strings defined in the
        app_settings.USER_TYPES setting.
    """
    session = _get_session(request)
    if session == None:
        return None
    else:
        return session.user.type

#############################################################################

def get_login_url():
    """ Return the URL for the "login" page.
    """
    return reverse(app_settings.APP_MODULE_PATH + ".views.login.login")

#############################################################################

def get_logout_url():
    """ Return the URL for the "logout" page.
    """
    return reverse(app_settings.APP_MODULE_PATH + ".views.logout.logout")

#############################################################################

def get_change_password_url():
    """ Return the URL for the "change password" page.
    """
    return reverse(app_settings.APP_MODULE_PATH + ".views.password.password")

#############################################################################

def get_user_admin_url():
    """ Return the URL for the "user admin" page.
    """
    return reverse(app_settings.APP_MODULE_PATH + ".views.admin.main")

#############################################################################

def redirect_to_login():
    """ Return an HttpResponseRedirect object redirecting to the login page.
    """
    return HttpResponseRedirect(get_login_url())

#############################################################################

def redirect_to_logout():
    """ Return an HttpResponseRedirect object redirecting to the logout page.
    """
    return HttpResponseRedirect(get_logout_url())

#############################################################################

def redirect_to_password_reset():
    """ Return HttpResponseRedirect object redirecting to password reset page.
    """
    return HttpResponseRedirect(get_password_reset_url())

#############################################################################

def redirect_to_user_admin():
    """ Return HttpResponseRedirect object redirecting to the user admin page.
    """
    return HttpResponseRedirect(get_user_admin_url())

#############################################################################
#                                                                           #
#                    P R I V A T E   D E F I N I T I O N S                  #
#                                                                           #
#############################################################################

def _get_session(request):
    """ Return the Session object associated with the given HttpRequest.

        We update the Session's last_access time so that we remember when the
        session was last accessed.

        If there is no valid session for this request, we return None.
    """
    session_token = request.session.get("authentication_session_token")
    if session_token == None:
        return None

    try:
        session = Session.objects.get(session_token=session_token)
    except Session.DoesNotExist:
        return None

    now = timezone.now()
    age = now - session.last_access
    if age > datetime.timedelta(seconds=app_settings.MAX_IDLE_TIME):
        # Session timed out -> delete it.
        session.delete()
        return None

    session.last_access = now
    session.save()

    return session

