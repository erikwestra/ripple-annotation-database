""" authentication.views.admin

    This module defines the user-administration views for the Authentication
    app.
"""
from django.http              import HttpResponse, HttpResponseRedirect
from django.shortcuts         import render
from django.core.urlresolvers import reverse

from ..       import auth_controller
from ..       import app_settings
from ..models import *

#############################################################################

def main(request):
    """ Respond to the main "admin" URL.

        We display a list of users, with options to add/edit/delete users.
    """
    if not auth_controller.is_logged_in(request):
        return HttpResponseRedirect(app_settings.MAIN_URL)

    if not auth_controller.is_admin(request):
        return HttpResponseRedirect(app_settings.MAIN_URL)

    users = []
    for user in User.objects.all().order_by("username"):
        users.append(user)

    cur_username = auth_controller.get_username(request)

    add_path    = app_settings.APP_MODULE_PATH + ".views.admin.add_user"
    edit_path   = app_settings.APP_MODULE_PATH + ".views.admin.edit_user"
    delete_path = app_settings.APP_MODULE_PATH + ".views.admin.delete_user"

    add_url      = reverse(add_path)
    edit_url     = reverse(edit_path)
    delete_url   = reverse(delete_path)
    finished_url = app_settings.MAIN_URL

    return render(request, "authentication/admin.html",
                  {'users'        : users,
                   'cur_username' : cur_username,
                   'add_url'      : add_url,
                   'edit_url'     : edit_url,
                   'delete_url'   : delete_url,
                   'finished_url' : finished_url})

#############################################################################

def add_user(request):
    """ Respond to the "admin/add_user" URL.

        We let the administrator add a new user to the system.
    """
    if not auth_controller.is_logged_in(request):
        return HttpResponseRedirect(app_settings.MAIN_URL)

    if not auth_controller.is_admin(request):
        return HttpResponseRedirect(app_settings.MAIN_URL)

    if request.method == "GET":
        # We're displaying the page for the first time -> set up our defaults.

        username  = ""
        user_type = app_settings.DEFAULT_USER_TYPE
        err_msg   = None

    elif request.method == "POST":

        if request.POST.get("cancel") != None:
            return auth_controller.redirect_to_user_admin()

        if request.POST.get("submit") != None:

            err_msg = None # initially.

            username = request.POST['username']
            if username == "":
                err_msg = "You must enter a username."

            if err_msg == None:
                try:
                    existing_user = User.objects.get(username__iexact=username)
                except User.DoesNotExist:
                    existing_user = None

                if existing_user != None:
                    err_msg = "There is already a user with that username."

            user_type = request.POST['user_type']
            if user_type == "":
                err_msg = "You must enter a type."

            if err_msg == None:
                password_1 = request.POST['password_1']
                if password_1 == "":
                    err_msg = "You must enter a password."

            if err_msg == None:
                password_2 = request.POST['password_2']
                if password_1 != password_2:
                    err_msg = "The entered passwords do not match."

            if err_msg == None:
                # Success!  Save this user.
                user = User()
                user.username = username
                user.type     = user_type
                user.set_password(password_1)
                user.save()

                return auth_controller.redirect_to_user_admin()

    # If we get here, display the "add user" page.

    return render(request, "authentication/edit.html",
                  {'title'        : "Add User",
                   'heading'      : "Add User",
                   'username'     : username,
                   'user_type'    : user_type,
                   'user_types'   : app_settings.USER_TYPES,
                   'can_set_type' : True,
                   'err_msg'      : err_msg})

#############################################################################

def edit_user(request, user_id=None):
    """ Respond to the "admin/edit_user/X" URL.

        We let the administrator edit the user with the given record ID.
    """
    if not auth_controller.is_logged_in(request):
        return HttpResponseRedirect(app_settings.MAIN_URL)

    if not auth_controller.is_admin(request):
        return HttpResponseRedirect(app_settings.MAIN_URL)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        user = None

    if user == None: # Should never happen.
        return HttpResponseRedirect(app_settings.MAIN_URL)

    can_set_type = (user.username != auth_controller.get_username(request))

    if request.method == "GET":
        # We're displaying the page for the first time -> set up our defaults.

        username  = user.username
        user_type = user.type
        err_msg   = None

    elif request.method == "POST":

        if request.POST.get("cancel") != None:
            return auth_controller.redirect_to_user_admin()

        if request.POST.get("submit") != None:

            err_msg = None # initially.

            username = request.POST['username']
            if username == "":
                err_msg = "You must enter a username."

            if err_msg == None:
                try:
                    existing_user = User.objects.get(username__iexact=username)
                except User.DoesNotExist:
                    existing_user = None

                if existing_user != None and existing_user != user:
                    err_msg = "There is already a user with that username."

            if can_set_type:
                user_type = request.POST['user_type']
                if user_type == "":
                    err_msg = "You must enter a type."

            if err_msg == None:
                password_1 = request.POST['password_1']
                password_2 = request.POST['password_2']
                if password_1 != "" and password_1 != password_2:
                    err_msg = "The entered passwords do not match."

            if err_msg == None:
                # Success!  Save the updated user details.
                user.username = username
                if can_set_type:
                    user.type = user_type
                if password_1 != "":
                    user.set_password(password_1)
                user.save()

                return auth_controller.redirect_to_user_admin()

    # If we get here, display the "add user" page.

    return render(request, "authentication/edit.html",
                  {'title'        : "Edit User",
                   'heading'      : "Edit User",
                   'username'     : username,
                   'user_type'    : user_type,
                   'user_types'   : app_settings.USER_TYPES,
                   'can_set_type' : can_set_type,
                   'err_msg'      : err_msg})

#############################################################################

def delete_user(request, user_id=None):
    """ Respond to the "admin/delete_user/X" URL.

        We let the administrator delete the use with the given record ID.
    """
    if not auth_controller.is_logged_in(request):
        return HttpResponseRedirect(app_settings.MAIN_URL)

    if not auth_controller.is_admin(request):
        return HttpResponseRedirect(app_settings.MAIN_URL)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        user = None

    if user == None: # Should never happen.
        return HttpResponseRedirect(app_settings.MAIN_URL)

    if request.method == "POST":
        if request.POST.get("confirm") == "1":
            user.delete()
        return auth_controller.redirect_to_user_admin()

    return render(request, "authentication/delete.html",
                  {'username' : user.username})
