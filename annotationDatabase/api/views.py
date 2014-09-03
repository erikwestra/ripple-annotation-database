""" annotationDatabase.api.views

    This module defines the various view functions for the Ripple Annotation
    Database's "api" application.

    Note that these are just wrappers around the equivalent functions provided
    by the annotationDatabase.api.functions module.
"""
from django.http import HttpResponse, HttpResponseNotAllowed

import simplejson as json

from annotationDatabase.api import functions, helpers

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

    if not helpers.auth_token_valid(batch.get("auth_token")):
        return HttpResponse(json.dumps({'success' : False,
                                        'error'   : 'Invalid or missing ' +
                                                    'authentication token'}),
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

    if not helpers.auth_token_valid(params.get("auth_token")):
        return HttpResponse(json.dumps({'success' : False,
                                        'error'   : 'Invalid or missing ' +
                                                    'authentication token'}),
                            content_type="application/json")

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

    if not helpers.auth_token_valid(params.get("auth_token")):
        return HttpResponse(json.dumps({'success' : False,
                                        'error'   : 'Invalid or missing ' +
                                                    'authentication token'}),
                            content_type="application/json")

    page = params.get("page", 1)
    rpp  = params.get("rpp",  100)

    response = functions.list_batches(page, rpp)

    return HttpResponse(json.dumps(response), content_type="application/json")

#############################################################################

def get(request, batch_number):
    """ Respond to the "/get/{batch_number}" URL.
    """
    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

    if not helpers.auth_token_valid(params.get("auth_token")):
        return HttpResponse(json.dumps({'success' : False,
                                        'error'   : 'Invalid or missing ' +
                                                    'authentication token'}),
                            content_type="application/json")

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

    if not helpers.auth_token_valid(params.get("auth_token")):
        return HttpResponse(json.dumps({'success' : False,
                                        'error'   : 'Invalid or missing ' +
                                                    'authentication token'}),
                            content_type="application/json")

    page = params.get("page", 1)
    rpp  = params.get("rpp",  100)

    response = functions.list_accounts(page, rpp)
    return HttpResponse(json.dumps(response), content_type="application/json")

#############################################################################

def account(request, account):
    """ Respond to the "/account/{account}" URL.
    """
    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

    if not helpers.auth_token_valid(params.get("auth_token")):
        return HttpResponse(json.dumps({'success' : False,
                                        'error'   : 'Invalid or missing ' +
                                                    'authentication token'}),
                            content_type="application/json")

    response = functions.account(account)

    return HttpResponse(json.dumps(response), content_type="application/json")

#############################################################################

def account_history(request, account):
    """ Respond to the "/account_history/{account}" URL.
    """
    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

    if not helpers.auth_token_valid(params.get("auth_token")):
        return HttpResponse(json.dumps({'success' : False,
                                        'error'   : 'Invalid or missing ' +
                                                    'authentication token'}),
                            content_type="application/json")

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

    if "auth_token" not in params:
        public_only = True
    else:
        public_only = False

    if not public_only:
        if not helpers.auth_token_valid(params.get("auth_token")):
            return HttpResponse(json.dumps({'success' : False,
                                            'error'   : 'Invalid or missing ' +
                                                        'authentication ' +
                                                        'token'}),
                                content_type="application/json")

    if "query" in params:
        query = params['query']
    else:
        return HttpResponse(json.dumps({'success' : False,
                                        'error'   : 'Missing required ' +
                                                    '"query" parameter'}),
                            content_type="application/json")


    if "page" in params:
        page = params['page']
    else:
        page = 1

    if "rpp" in params:
        rpp = params['rpp']
    else:
        rpp = 1000

    if "totals_only" in params:
        totals_only = (params['totals_only'] == "1")
    else:
        totals_only = False

    response = functions.search(query=query, page=page, rpp=rpp,
                                totals_only=totals_only,
                                public_only=public_only)

    return HttpResponse(json.dumps(response), content_type="application/json")

#############################################################################

def set_template(request, template_name):
    """ Respond to the "/set_template/{template}" URL.
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

        if "template" not in params:
            return HttpResponse(json.dumps({'success' : False,
                                            'error'   : 'Missing required ' +
                                                        '"template" ' +
                                                        'parameter'}),
                                content_type="application/json")

        raw_data = params['template']

    try:
        template = json.loads(raw_data)
    except ValueError:
        return HttpResponse(json.dumps({'success' : False,
                                        'error'   : 'Invalid JSON data'}),
                            content_type="application/json")

    if not helpers.auth_token_valid(template.get("auth_token")):
        return HttpResponse(json.dumps({'success' : False,
                                        'error'   : 'Invalid or missing ' +
                                                    'authentication token'}),
                            content_type="application/json")

    response = functions.set_template(template_name, template['template'])

    return HttpResponse(json.dumps(response), content_type="application/json")

#############################################################################

def get_template(request, template_name):
    """ Respond to the "/get_template/{template}" URL.
    """
    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

    if not helpers.auth_token_valid(params.get("auth_token")):
        return HttpResponse(json.dumps({'success' : False,
                                        'error'   : 'Invalid or missing ' +
                                                    'authentication token'}),
                            content_type="application/json")

    response = functions.get_template(template_name)

    return HttpResponse(json.dumps(response), content_type="application/json")

#############################################################################

def public_annotations(request):
    """ Respond to the "public_annotations" URL.
    """
    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

    if "annotation" not in params:
        return HttpResponse(json.dumps({'success' : False,
                                        'error'   : 'Missing required ' +
                                                    '"annotation" ' +
                                                    'parameter'}),
                            content_type="application/json")
    annotation = params['annotation']
    page       = params.get("page", 1)
    rpp        = params.get("rpp",  100)

    response = functions.public_annotations(annotation, page=page, rpp=rpp)

    return HttpResponse(json.dumps(response), content_type="application/json")
    
