""" authentication.views.login

    This module defines the "login" view for the Authentication app.
"""
import uuid

from django.http      import HttpResponseRedirect
from django.shortcuts import render
from django.utils     import timezone

from ..       import auth_controller
from ..       import app_settings
from ..models import *

#############################################################################

def login(request):
    """ Respond to the "login" URL.

        We ask the user to log in.
    """
    if auth_controller.is_logged_in(request):
        return HttpResponseRedirect(app_settings.MAIN_URL)

    if request.method == "GET":
        # We're displaying this page for the first time -> set up the defaults.

        username = ""
        err_msg  = None

    elif request.method == "POST":

        if request.POST.get("cancel") != None:
            # The user cancelled -> return back to the main page.
            return HttpResponseRedirect(app_settings.MAIN_URL)

        if request.POST.get("submit") != None:
            # The user submitted the form -> check the entered values.

            err_msg = None # initially.

            username = request.POST.get("username")
            if username == "":
                err_msg = "Please enter a username."

            if err_msg == None:
                try:
                    user = User.objects.get(username__iexact=username)
                except User.DoesNotExist:
                    user = None

                password = request.POST.get("password")
                if user == None or not user.is_password_correct(password):
                    err_msg = "Incorrect username or password"

            if err_msg == None:
                # Success!  Create a session for this user, logging them in.

                session_token = uuid.uuid4().hex

                session = Session()
                session.session_token = session_token
                session.user          = user
                session.last_access   = timezone.now()
                session.save()

                request.session['authentication_session_token'] = session_token

                # Finally, redirect the user back to the main page.

                return HttpResponseRedirect(app_settings.MAIN_URL)

    # If we get here, display the "login" page.

    return render(request, "authentication/login.html",
                  {'heading'  : app_settings.LOGIN_HEADING,
                   'username' : username,
                   'err_msg'  : err_msg,
                  })

