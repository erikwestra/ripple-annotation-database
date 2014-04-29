""" annotationDatabase.api.views

    This module defines the various view functions for the Ripple Annotation
    Database's "api" application.

    Note that these are just wrappers around the equivalent functions provided
    by the annotationDatabase.api.functions module.
"""
from django.http import HttpResponse, HttpResponseNotAllowed

import simplejson as json

from annotationDatabase.api import functions

#############################################################################

def add(request):
    """ Respond to the "/add" URL.
    """
    if (request.method == "POST" and
        ("application/json" in request.META['CONTENT_TYPE'])):
        raw_data = request.body
    else:
        if request.method == "GET":
            params = request.GET
        elif request.method == "POST":
            params = request.POST
        else:
            return HttpResponseNotAllowed(["GET", "POST"])

        if "batch" not in params:
            return HttpResponse(json.dumps({'success' : False,
                                            'error'   : 'Missing required ' +
                                                        '"batch" parameter'}),
                                content_type="application/json")

        raw_data = params['batch']

    try:
        batch = json.loads(raw_data)
    except ValueError:
        return HttpResponse(json.dumps({'success' : False,
                                        'error'   : 'Invalid JSON data'}),
                            content_type="application/json")

    response = functions.add(batch)

    return HttpResponse(json.dumps(response), content_type="application/json")

#############################################################################

def hide(request):
    """ Respond to the "/hide" URL.
    """
    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

    if "user_id" not in params:
        return HttpResponse(json.dumps({'success' : False,
                                        'error'   : 'Missing required ' +
                                                    '"user_id" parameter'}),
                            content_type="application/json")
    else:
        user_id = params['user_id']

    if "batch_num" not in params:
        return HttpResponse(json.dumps({'success' : False,
                                        'error'   : 'Missing required ' +
                                                    '"batch_num" parameter'}),
                            content_type="application/json")
    else:
        batch_num = params['batch_num']

    account = params.get("account")
    annotation = params.get("annotation")

    response = functions.hide(user_id, batch_num, account, annotation)

    return HttpResponse(json.dumps(response), content_type="application/json")

#############################################################################

def list(request):
    """ Respond to the "/list" URL.
    """
    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

    page = params.get("page", 1)
    rpp  = params.get("rpp",  100)

    response = functions.list_batches(page, rpp)

    return HttpResponse(json.dumps(response), content_type="application/json")

#############################################################################

def get(request, batch_number):
    """ Respond to the "/get/{batch_number}" URL.
    """
    response = functions.get(batch_number)
    return HttpResponse(json.dumps(response), content_type="application/json")

#############################################################################

def accounts(request):
    """ Respond to the "/account/{account}" URL.
    """
    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

    page = params.get("page", 1)
    rpp  = params.get("rpp",  100)

    response = functions.list_accounts(page, rpp)
    return HttpResponse(json.dumps(response), content_type="application/json")

#############################################################################

def account(request, account):
    """ Respond to the "/account/{account}" URL.
    """
    response = functions.account(account)
    return HttpResponse(json.dumps(response), content_type="application/json")

#############################################################################

def account_history(request, account):
    """ Respond to the "/account_history/{account}" URL.
    """
    response = functions.account_history(account)
    return HttpResponse(json.dumps(response), content_type="application/json")

#############################################################################

def search(request):
    """ Respond to the "/search" URL.
    """
    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

    if len(params) > 3:
        return HttpResponse(json.dumps({'success' : False,
                                        'error'   : 'Too many search criteria'
                                       }),
                            content_type="application/json")

    criteria = []
    for key in params.keys():
        value = params[key]
        criteria.append([key, value])

    response = functions.search(criteria)
    return HttpResponse(json.dumps(response), content_type="application/json")

