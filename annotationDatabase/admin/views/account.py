""" annotationDatabase.admin.views.account

    This module implements the various account-related views for the
    annotationDatabase.admin application.
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

def view_current(request, account):
    """ Respond to the "/admin/account/{account}/current" URL.

        We let the user view the annotations associated with the given account.
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

    back_url = backHandler.get_back_param(request, default="/admin")

    response = functions.account(account)
    if not response['success']:
        return HttpResponseRedirect(back_url)

    paginator = Paginator(response['annotations'], 20)

    try:
        annotations = paginator.page(page)
    except PageNotAnInteger:
        annotations = paginator.page(1)
    except EmptyPage:
        annotations = []

    return render(request, "admin/view_current.html",
                  {'menus'        : get_admin_menus(request),
                   'current_url'  : "/admin/accounts/XXX/current",
                   'page_heading' : "Ripple Annotation Database Admin",
                   'page'         : page,
                   'num_pages'    : paginator.num_pages,
                   'account'      : account,
                   'annotations'  : annotations,
                   'back'         : backHandler.encode_current_url(request),
                   'done_url'     : back_url})

#############################################################################

def view_history(request, account):
    """ Respond to the "/admin/accounts/{account}/history" URL.

        We let the user view the history of all annotation changes made to the
        given account.
    """
    print "History!"

    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponse("Bad HTTP Method")

    page = int(params.get("page", "1"))

    back_url = backHandler.get_back_param(request, default="/admin")

    response = functions.account_history(account)
    if not response['success']:
        return HttpResponseRedirect(back_url)

    # Convert the account history to a list form for display.

    history_list = [] # List of values to display.  Each item is a dictionary
                      # with the following values:
                      #
                      #    'timestamp'
                      #
                      #        The date and time at which the annotation value
                      #        was set or hidden, as an integer number of
                      #        seconds since midnight on the 1st of January,
                      #        1970 ("unix time"), in UTC.
                      #
                      #    'batch_number'
                      #
                      #        The batch number where this annotation was set
                      #        or hidden.
                      #
                      #    'action'
                      #
                      #        The type of action.  One of "set" or "hide".
                      #
                      #    'user_id'
                      #
                      #        The user ID of the user who set or hid this
                      #        annotation value.
                      #
                      #    'key'
                      #
                      #        The annotation key.
                      #
                      #    'value'
                      #
                      #        The annotation value.

    for annotation in response['annotations']:
        key = annotation['key']
        for change in reversed(annotation['history']):
            history_list.append({'action'       : "set",
                                 'key'          : annotation['key'],
                                 'value'        : change['value'],
                                 'batch_number' : change['batch_number'],
                                 'user_id'      : change['user_id'],
                                 'timestamp'    : change['timestamp']})

            if change['hidden']:
                history_list.append({'action'       : "hide",
                                     'key'          : annotation['key'],
                                     'value'        : change['value'],
                                     'batch_number' : change['batch_number'],
                                     'user_id'      : change['hidden_by'],
                                     'timestamp'    : change['hidden_at']})

    for history in history_list:
        timestamp = history['timestamp']
        timestamp = datetime.datetime.utcfromtimestamp(timestamp)
        history['timestamp'] = timestamp

    # Paginate the history list, as required.

    paginator = Paginator(history_list, 20)

    try:
        history = paginator.page(page)
    except PageNotAnInteger:
        history = paginator.page(1)
    except EmptyPage:
        history = []

    return render(request, "admin/view_history.html",
                  {'menus'        : get_admin_menus(request),
                   'current_url'  : "/admin/accounts/XXX/history",
                   'page_heading' : "Ripple Annotation Database Admin",
                   'page'         : page,
                   'num_pages'    : paginator.num_pages,
                   'account'      : account,
                   'history'      : history,
                   'back'         : backHandler.encode_current_url(request),
                   'done_url'     : back_url})

