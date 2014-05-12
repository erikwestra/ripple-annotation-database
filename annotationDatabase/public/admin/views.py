""" annotationDatabase.public.admin.views

    This module defines the various administration views for the "public"
    application.
"""
import datetime
import uuid

from django.http           import HttpResponse, HttpResponseRedirect
from django.shortcuts      import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from annotationDatabase.authentication import auth_controller

from annotationDatabase.public.models import *

from annotationDatabase.api import functions

#############################################################################

def user_admin(request):
    """ Respond to the "/admin/public/users" URL.

        We let the user view and edit the list of public users of the
        Annotation Database.  We can block and delete users as desired.
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

    if request.method == "POST":
        if request.POST['submit'] == "Done":
            return HttpResponseRedirect("/admin")

    return render(request, "public/user_admin.html",
                  {'page'      : page,
                   'num_pages' : paginator.num_pages,
                   'users'     : users})

#############################################################################

def block_user(request, user_id):
    """ Respond to the "/admin/public/users/block/XXX" URL.

        We block the given user.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponse("Bad HTTP Method")

    if "page" in params:
        user_admin_url = "/admin/public/users?page=" + params['page']
    else:
        user_admin_url = "/admin/public/users"

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponseRedirect(user_admin_url)

    user.blocked = True
    user.save()

    return HttpResponseRedirect(user_admin_url)

#############################################################################

def unblock_user(request, user_id):
    """ Respond to the "/admin/public/users/unblock/XXX" URL.

        We unblock the given user.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponse("Bad HTTP Method")

    if "page" in params:
        user_admin_url = "/admin/public/users?page=" + params['page']
    else:
        user_admin_url = "/admin/public/users"

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponseRedirect(user_admin_url)

    user.blocked = False
    user.save()

    return HttpResponseRedirect(user_admin_url)

#############################################################################

def delete_user(request, user_id):
    """ Respond to the "/admin/public/users/delete/XXX" URL.

        We delete the given user.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        # Should never happen.
        return HttpResponseRedirect("/admin/public/users")

    if request.method == "POST":
        if request.POST['submit'] == "Delete":
            # The user confirmed -> delete the user.
            user.delete()

        return HttpResponseRedirect("/admin/public/users")

    # Display the confirmation dialog.

    return render(request, "public/confirm.html",
                  {'heading'  : "Delete Public User",
                   'message'  : 'Are you sure you want to delete the "' +
                                user.username + '" user?',
                   'btn_name' : "Delete"})

#############################################################################

def account_admin(request):
    """ Respond to the "/admin/public/accounts" URL.

        We let the user view and edit the list of public accounts for the
        Annotation Database.  We can view and remove account ownership claims
        as desired.
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

    all_accounts = Account.objects.all().order_by("owner__username", "address")

    paginator = Paginator(all_accounts, 20)

    try:
        accounts = paginator.page(page)
    except PageNotAnInteger:
        accounts = paginator.page(1)
    except EmptyPage:
        accounts = []

    if request.method == "POST":
        if request.POST['submit'] == "Done":
            return HttpResponseRedirect("/admin")

    return render(request, "public/account_admin.html",
                  {'page'      : page,
                   'num_pages' : paginator.num_pages,
                   'accounts'  : accounts})

#############################################################################

def delete_account(request, account_id):
    """ Respond to the "/admin/public/accounts/delete/XXX" URL.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    try:
        account = Account.objects.get(id=account_id)
    except Account.DoesNotExist:
        # Should never happen.
        return HttpResponseRedirect("/admin/public/accounts")

    if request.method == "POST":
        if request.POST['submit'] == "Delete":
            # The user confirmed -> delete the account.
            account.delete()

        return HttpResponseRedirect("/admin/public/accounts")

    # Display the confirmation dialog.

    return render(request, "public/confirm.html",
                  {'heading'  : "Delete Public User Account",
                   'message'  : 'Are you sure you want to delete the "' +
                                account.address + '" account for user ' +
                                account.owner.username + "?  Doing this " +
                                "won't remove the account's annotations, " +
                                "but will let another user claim ownership " +
                                "of that account.",
                   'btn_name' : "Delete"})

