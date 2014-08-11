""" annotationDatabase.admin.views.user

    This module implements the various user-related view functions for the
    Ripple Annotation Database's "admin" application.
"""
import csv
import datetime
import urllib
import uuid

import simplejson as json
import xlrd

from django.http           import HttpResponse, HttpResponseRedirect
from django.shortcuts      import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from annotationDatabase.authentication import auth_controller

from annotationDatabase.shared.models import *
from annotationDatabase.shared.lib    import logicalExpressions, backHandler

from annotationDatabase.api import functions

from annotationDatabase.admin.menus import get_admin_menus

#############################################################################

def list(request):
    """ Display a list of the signed-up users in the system.

        Note that this is the top-level URL for the admin application.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponse("Bad HTTP Method")

    page = int(params.get("page", "1"))

    all_users = User.objects.all().order_by("username")

    paginator = Paginator(all_users, 20)

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = []

    return render(request, "admin/new_user_list.html",
                  {'menus'        : get_admin_menus(request),
                   'current_url'  : "/admin",
                   'page_heading' : "Ripple Annotation Database Admin",
                   'page'         : page,
                   'num_pages'    : paginator.num_pages,
                   'users'        : users,
                   'back'         : backHandler.encode_current_url(request)})

#############################################################################

def accounts(request, user_id):
    """ Respond to the "/admin/user/XXX/accounts" URL.

        We display the list of accounts owned by the given user.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    back_url = backHandler.get_back_param(request, default="/admin")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponseRedirect(back_url) # Should never happen.

    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponse("Bad HTTP Method")

    page = int(params.get("page", "1"))

    all_accounts = Account.objects.filter(owner=user).order_by("address")

    paginator = Paginator(all_accounts, 20)

    try:
        accounts = paginator.page(page)
    except PageNotAnInteger:
        accounts = paginator.page(1)
    except EmptyPage:
        accounts = []

    return render(request, "admin/new_user_accounts.html",
                  {'menus'        : get_admin_menus(request),
                   'current_url'  : "/admin/user/XXX/accounts",
                   'page_heading' : "Ripple Annotation Database Admin",
                   'page'         : page,
                   'num_pages'    : paginator.num_pages,
                   'user'         : user,
                   'accounts'     : accounts,
                   'back'         : backHandler.encode_current_url(request),
                   'done_url'     : back_url})

#############################################################################

def block(request, user_id):
    """ Respond to the "/admin/user/XXX/block" URL.

        We block the given user.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    back_url = backHandler.get_back_param(request, default="/admin")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        user = None

    if user != None:
        user.blocked = True
        user.save()

    return HttpResponseRedirect(back_url)

#############################################################################

def unblock(request, user_id):
    """ Respond to the "/admin/user/XXX/unblock" URL.

        We unblock the given user.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    back_url = backHandler.get_back_param(request, default="/admin")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        user = None

    if user != None:
        user.blocked = False
        user.save()

    return HttpResponseRedirect(back_url)

#############################################################################

def delete(request, user_id):
    """ Respond to the "/admin/user/XXX/delete" URL.

        We delete the given user, after confirming with the user.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    back_url = backHandler.get_back_param(request, default="/admin")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponseRedirect(back_url) # Should never happen.

    if request.method == "POST":
        if request.POST['submit'] == "Submit":
            # The user clicked on our "Submit" button -> delete the user.
            for account in Account.objects.filter(owner=user):
                account.owner = None
                account.save()
            user.delete()

        return HttpResponseRedirect(back_url)

    # Display the confirmation dialog.

    encoded_url = backHandler.encode_url(back_url)
    return render(request, "admin/new_confirm.html",
                  {'menus'         : get_admin_menus(request),
                   'current_url'   : "/admin/user/%s/delete" % user_id,
                   'heading'       : "Delete User",
                   'message'       : "Are you sure you want to delete the " +
                                     '"' + user.username + '" ' +
                                     "user?  The user's account annotations " +
                                     "won't be deleted, and another user " +
                                     "can claim these accounts.",
                   'hidden_vars'   : dict(back=encoded_url),
                   'submit_label'  : "Delete"})

#############################################################################

def remove_account(request, user_id, account):
    """ Respond to the "/admin/user/XXX/remove/YYY" URL.

        We remove the given account from the user.  This doesn't delete the
        account, but makes it available for another user to claim it.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    back_url = backHandler.get_back_param(request, default="/admin")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponseRedirect(back_url) # Should never happen.

    try:
        account = Account.objects.get(address=account)
    except Account.DoesNotExist:
        return HttpResponseRedirect(back_url) # Should never happen.

    if account.owner != user:
        return HttpResponseRedirect(back_url) # Should never happen.

    if request.method == "POST":
        if request.POST['submit'] == "Submit":
            # The user clicked on our "Submit" button -> remove the account
            # from this user.
            account.owner = None
            account.save()

        return HttpResponseRedirect(back_url)

    # Display the confirmation dialog.

    encoded_url = backHandler.encode_url(back_url)
    return render(request, "admin/new_confirm.html",
                  {'menus'         : get_admin_menus(request),
                   'current_url'   : "/admin/user/%s/delete" % user_id,
                   'heading'       : "Remove Account",
                   'message'       : "Are you sure you want to remove the " +
                                     '"' + account.address + '"' +
                                     "account for user " +
                                     '"' + user.username + '"' + 
                                     "?  The user's account annotations " +
                                     "won't be deleted, and another user " +
                                     "can claim this account.",
                   'hidden_vars'   : dict(back=encoded_url),
                   'submit_label'  : "Remove"})

