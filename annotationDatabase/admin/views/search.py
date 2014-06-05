""" annotationDatabase.admin.views.search

    This module defines the various search-related views for the
    annotationDatabase.admin application.
"""
import csv

from django.http      import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from annotationDatabase.authentication import auth_controller

from annotationDatabase.shared.models import *
from annotationDatabase.shared.lib    import logicalExpressions, backHandler

from annotationDatabase.api import functions

from annotationDatabase.admin.menus import get_admin_menus

#############################################################################

def search(request):
    """ Respond to the "/admin/search" URL.

        We let the user search for accounts with a given set of annotation
        values.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    if request.method == "GET":
        # This is the first time we've displayed this page -> prepare our CGI
        # parameters.
        query   = ""
        err_msg = None

    elif request.method == "POST":

        if request.POST['submit'] == "Search":
            # The user is attempting to submit the form.  Extract the submitted
            # form data.
            err_msg = None # initially.

            query = request.POST.get("query", "")

            if query == "":
                err_msg = "You must enter a search query."

            if err_msg == None:
                expression = logicalExpressions.parse(query)
                if expression == None:
                    err_msg = "Sorry, that is not a valid search query."

            if err_msg == None:
                # Redirect the user to display the matching accounts.
                query = query.replace("&", "%26")
                query = query.replace("=", "%3D")
                return HttpResponseRedirect("/admin/search/results" +
                                            "?query=" + query)
        elif request.POST['submit'] == "Cancel":
            return HttpResponseRedirect("/admin")

    return render(request, "admin/new_search.html", 
                  {'title'         : "Ripple Annotation Database",
                   'heading'       : "Admin Interface",
                   'menus'         : get_admin_menus(request),
                   'current_url'   : "/admin/search",
                   'query'         : query,
                   'err_msg'       : err_msg,
                   'done_url'      : "/admin",
                  })

#############################################################################

def search_results(request):
    """ Respond to the "/admin/search/results" URL.

        We display the matching accounts for a given set of search criteria.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponse("Bad HTTP Method")

    err_msg  = None # initially.
    page     = params.get("page", 1)
    query    = params.get("query", "")
    download = params.get("download", "")

    if request.method == "POST" and request.POST['submit'] == "Search":
        # The user pressed the "Search" button -> reissue the search request.
        query = query.replace("&", "%26")
        query = query.replace("=", "%3D")
        return HttpResponseRedirect("/admin/search/results" +
                                    "?query=" + query)

    if download == "1":
        # The user clicked on our "Download Search Results" button.  Return the
        # search results as a CSV file to download.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="results.csv"'

        search_results = _download_search_results(query)

        writer = csv.writer(response)
        for row in search_results:
            writer.writerow(row)

        return response

    response = functions.search(query, page, rpp=15, totals_only=False)
    if not response['success']:
        err_msg = response['error']

    return render(request, "admin/new_search_results.html",
                  {'menus'       : get_admin_menus(request),
                   'current_url' : "/admin/search",
                   'query'       : query,
                   'num_matches' : response.get('num_matches', 0),
                   'num_pages'   : response.get('num_pages', 1),
                   'err_msg'     : err_msg,
                   'page'        : page,
                   'accounts'    : response.get('accounts', []),
                   'done_url'      : "/admin",
                  })

#############################################################################
#                                                                           #
#                    P R I V A T E   D E F I N I T I O N S                  #
#                                                                           #
#############################################################################

def _download_search_results(query):
    """ Download the search results for the given search query.

        We return a list of lines of data to return, where each list item is
        itself a list of the individual values in each row.
    """
    lines = [] # List of list of strings.
    row = []
    row.append("Search Query:")
    row.append(query)
    lines.append(row)

    first = True
    page  = 1

    while True:
        response = functions.search(query, page)
        if not response['success']:
            lines.append(["Server Error:", response['error']])
            break

        for account in response['accounts']:
            row = []
            if first:
                row.append("Matching Accounts")
                first = False
            else:
                row.append("")
            row.append(account)
            lines.append(row)

        if page <= response['num_pages']:
            page = page + 1
            continue
        else:
            break

    return lines

