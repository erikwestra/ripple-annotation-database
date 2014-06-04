""" authentication.views.password

    This module defines the "change password" view for the Authentication app.
"""
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ..       import auth_controller
from ..       import app_settings
from ..models import *

#############################################################################

def password(request):
    """ Respond to the "change password" URL.

        We let the user change their password.
    """
    if not auth_controller.is_logged_in(request):
        return HttpResponseRedirect(app_settings.MAIN_URL)

    if request.method == "GET":
        # We're displaying this page for the first time -> set up the defaults.

        err_msg  = None

    elif request.method == "POST":

        if request.POST.get("submit") == "Cancel":
            # The user cancelled -> return back to the main page.
            return HttpResponseRedirect(app_settings.MAIN_URL)

        if request.POST.get("submit") == "Submit":
            # The user submitted the form -> check the entered values.

            err_msg = None # initially.

            username   = auth_controller.get_username(request)
            old_pass   = request.POST.get("old_pass")
            new_pass_1 = request.POST.get("new_pass_1")
            new_pass_2 = request.POST.get("new_pass_2")

            try:
                user = User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                user = None

            if user == None:
                # Should never happen.
                return HttpResponseRedirect(app_settings.MAIN_URL)

            if not user.is_password_correct(old_pass):
                err_msg = "Incorrect password."

            if err_msg == None:
                if new_pass_1 == "":
                    err_msg = "You must enter a new password."

            if err_msg == None:
                if new_pass_1 != new_pass_2:
                    err_msg = "The entered passwords do not match."

            if err_msg == None:
                # Success!  Change the user's password.
                user.set_password(new_pass_1)
                user.save()
                return HttpResponseRedirect(app_settings.MAIN_URL)

    # If we get here, display the "change password" page.

    return render(request, "authentication/new_change_password.html",
                  {'shortcut_icon' : app_settings.SHORTCUT_ICON,
                   'heading_icon'  : app_settings.HEADING_ICON,
                   'err_msg'       : err_msg})

