""" annotationDatabase.web.views

    This module defines the various view functions for the Ripple Annotation
    Database's "web" application.
"""
import datetime

import xlrd

from django.http           import HttpResponse, HttpResponseRedirect
from django.shortcuts      import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from annotationDatabase.authentication import auth_controller

from annotationDatabase.shared.models import *

from annotationDatabase.api import functions

#############################################################################

def main(request):
    """ Respond to our top-level "/web" URL.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    options = []
    options.append(["Add Annotations",          "/web/add"])
    options.append(["Upload Annotations",       "/web/upload"])
    options.append(["View Annotation Batches",  "/web/select_batch"])
    options.append(["View Account Annotations", "/web/select_account"])
    options.append(["Search",                   "/web/search"])
    options.append(["--------------", None])
    if auth_controller.is_admin(request):
        options.append(["Add/Edit Users",
                        auth_controller.get_user_admin_url()])
    options.append(["Change Password",
                    auth_controller.get_change_password_url()])
    options.append(["Log Out", auth_controller.get_logout_url()])

    return render(request, "web/main.html", {'options' : options})

#############################################################################

def add(request):
    """ Respond to the "/web/add" URL.

        We let the user manually add an annotation to the system.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    if request.method == "GET":
        # This is the first time we've displayed this page -> prepare our CGI
        # parameters.
        data = []
        for row in range(10):
            data.append({'account' : "",
                         'key'     : "",
                         'value'   : ""})

        err_msg = None

    elif request.method == "POST":

        if request.POST['submit'] == "Add":
            # The user is attempting to submit the form.  Extract the submitted
            # form data.

            err_msg = None # initially.

            data     = []
            bad_data = False # initially.
            for row in range(10):
                account = request.POST.get("account-%d" % row, "")
                key     = request.POST.get("key-%d" % row, "")
                value   = request.POST.get("value-%d" % row, "")

                data.append({'account' : account,
                             'key'     : key,
                             'value'   : value})

                if ((account != "" or key != "" or value != "") and
                    (account == "" or key == "" or value == "")):
                    bad_data = True

            if bad_data:
                err_msg = "You must enter all information on each row."

            if err_msg == None:
                annotations = []
                for row in data:
                    if (row['account'] != "" and
                        row['key'] != "" and
                        row['value'] != ""):
                        annotations.append(row)
                if len(annotations) == 0:
                    err_msg = "You haven't entered any data."

            if err_msg == None:
                # Save the entered annotation data into the system.
                user_id = auth_controller.get_username(request)

                response = functions.add({'user_id'     : user_id,
                                          'annotations' : annotations})
                if response['success']:
                    return HttpResponseRedirect("/web")
                else:
                    err_msg = response['error']
        elif request.POST['submit'] == "Cancel":
            return HttpResponseRedirect("/web")

    return render(request, "web/add.html", {'data'    : data,
                                            'err_msg' : err_msg})

#############################################################################

def upload(request):
    """ Respond to the "/web/upload" URL.

        We let the user upload a batch of annotations.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    if request.method == "GET":
        # We're displaying this page for the first time -> prepare our CGI
        # parameters.
        err_msg = None
    elif request.method == "POST":
        # The user is submitting the form.  Try extracting the uploaded file.
        err_msg = None # initially.
        file = request.FILES.get("file")
        if file == None:
            err_msg = "Please select a file to upload."

        if err_msg == None:
            contents = file.read()
            workbook = xlrd.open_workbook(file_contents=contents)
            if workbook == None:
                err_msg = "This doesn't appear to be an Excel spreadsheet."

        if err_msg == None:
            if len(workbook.sheets()) != 1:
                err_msg = "There must be exactly one sheet in the spreadsheet."

        if err_msg == None:
            sheet = workbook.sheets()[0]
            if sheet.ncols == 0:
                err_msg = "That spreadsheet is empty."

        def _get_text(cell):
            """ Extract the text from the given cell.

                Returns an empty string if the cell is empty.
            """
            if cell.ctype == xlrd.XL_CELL_EMPTY:
                return ""
            else:
                return str(cell.value)

        if err_msg == None:
            # Extract the annotations from the spreadsheet.
            annotations = [] # List of annotations to save.  Each list item is
                             # a dictionary with 'account', 'key' and 'value'
                             # entries.

            for row in range(sheet.nrows):
                account = _get_text(sheet.cell(row, 0))
                col = 1
                while col < sheet.ncols:
                    key   = _get_text(sheet.cell(row, col))
                    value = _get_text(sheet.cell(row, col+1))
                    if account != "" and key != "" and value != "":
                        annotations.append({'account' : account,
                                            'key'     : key,
                                            'value'   : value})
                    col = col + 2

            if len(annotations) == 0:
                err_msg = "There are no annotations in that spreadsheet."

        if err_msg == None:
            # Save the annotations to disk.
            user_id = auth_controller.get_username(request)

            response = functions.add({'user_id'     : user_id,
                                      'annotations' : annotations})

            if not response['success']:
                err_msg = response['error']

        if err_msg == None:
            return HttpResponseRedirect("/web")

    return render(request, "web/upload.html", {'err_msg' : err_msg})

#############################################################################

def select_batch(request):
    """ Respond to the "/web/select_batch" URL.

        We display a list of annotation batches, and let the user select the
        batch to view.
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

    response = functions.list_batches(params.get("page"), rpp=20)
    if not response['success']:
        print response # Fix error handling later.
        return HttpResponseRedirect("/web")

    batches   = response['batches']
    num_pages = response['num_pages']

    for batch in batches:
        timestamp = batch['timestamp']
        batch['timestamp'] = datetime.datetime.utcfromtimestamp(timestamp)

    if request.method == "POST" and request.POST['submit'] == "Done":
        return HttpResponseRedirect("/web")

    return render(request, "web/select_batch.html",
                  {'page'      : page,
                   'num_pages' : num_pages,
                   'batches'   : batches})

#############################################################################

def view_batch(request, batch_number):
    """ Respond to the "/web/view_batch/{batch_number}" URL.

        We display the contents of the given annotation batch, and let the user
        hide annotations within the batch.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    response = functions.get(batch_number)

    if not response['success']:
        print response # Fix error handling later.
        return HttpResponseRedirect("/web")

    annotations = response['annotations']
    for annotation in annotations:
        if annotation['hidden']:
            timestamp = annotation['hidden_at']
            timestamp = datetime.datetime.utcfromtimestamp(timestamp)
            annotation['hidden_at'] = timestamp

    if request.method == "POST":
        for i,annotation in enumerate(annotations):
            if request.POST.get("hide-%d" % i) == "Hide":
                # Hide this annotation.
                user_id = auth_controller.get_username(request)
                functions.hide(user_id, batch_number,
                               account=annotation['account'],
                               annotation=annotation['key'])
                # Reload the page to show the updated batch contents.
                return HttpResponseRedirect("/web/view_batch/%s" %
                                            batch_number)

        if request.POST.get("submit") == "Done":
            return HttpResponseRedirect("/web")

    return render(request, "web/view_batch.html",
                  {'annotations' : annotations})

#############################################################################

def select_account(request):
    """ Respond to the "/web/select_account" URL.

        We let the user choose an account to view.
        view the annotations associated with a single account.
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

    response = functions.list_accounts(params.get("page"), rpp=20)
    if not response['success']:
        print response # Fix error handling later.
        return HttpResponseRedirect("/web")

    accounts  = response['accounts']
    num_pages = response['num_pages']

    if request.method == "POST" and request.POST['submit'] == "Done":
        return HttpResponseRedirect("/web")

    return render(request, "web/select_account.html",
                  {'page'      : page,
                   'num_pages' : num_pages,
                   'accounts'  : accounts})

#############################################################################

def view_account(request, account):
    """ Respond to the "/web/view_account/{account}" URL.

        We let the user view the annotations associated with a single account.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponse("Bad HTTP Method")

    page = params.get("page", 1)

    response = functions.account(account)
    if not response['success']:
        print response # Fix error handling later.
        return HttpResponseRedirect("/web")

    paginator = Paginator(response['annotations'], 20)

    try:
        annotations = paginator.page(page)
    except PageNotAnInteger:
        annotations = paginator.page(1)
    except EmptyPage:
        annotations = []

    if request.method == "POST" and request.POST['submit'] == "Done":
        return HttpResponseRedirect("/web/select_account")

    return render(request, "web/view_account.html",
                  {'account'     : account,
                   'page'        : page,
                   'num_pages'   : paginator.num_pages,
                   'annotations' : annotations})

#############################################################################

def view_account_history(request, account):
    """ Respond to the "/web/view_account/{account}" URL.

        We let the user view the annotations associated with a single account.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponse("Bad HTTP Method")

    page = params.get("page", 1)

    response = functions.account_history(account)
    if not response['success']:
        print response # Fix error handling later.
        return HttpResponseRedirect("/web")

    # Convert the account history to a list form for display.

    history_list = [] # List of values to display.  Each item is a dictionary
                      # with the following values:
                      #
                      #    'action'
                      #
                      #        The type of action.  One of "set" or "hide".
                      #
                      #    'key'
                      #
                      #        The annotation key.
                      #
                      #    'value'
                      #
                      #        The annotation value.
                      #
                      #    'batch_number'
                      #
                      #        The batch number where this annotation was set
                      #        or hidden.
                      #
                      #    'user_id'
                      #
                      #        The user ID of the user who set or hid this
                      #        annotation value.
                      #
                      #    'timestamp'
                      #
                      #        The date and time at which the annotation value
                      #        was set or hidden, as an integer number of
                      #        seconds since midnight on the 1st of January,
                      #        1970 ("unix time"), in UTC.

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

    if request.method == "POST" and request.POST['submit'] == "Done":
        return HttpResponseRedirect("/web/select_account")

    return render(request, "web/view_account_history.html",
                  {'account'   : account,
                   'page'      : page,
                   'num_pages' : paginator.num_pages,
                   'history'   : history})

#############################################################################

def search(request):
    """ Respond to the "/web/search" URL.

        We let the user search for accounts with a given set of annotation
        values.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    if request.method == "GET":
        # This is the first time we've displayed this page -> prepare our CGI
        # parameters.
        data = []
        for row in range(3):
            data.append({'key'   : "",
                         'value' : ""})

        err_msg = None

    elif request.method == "POST":

        if request.POST['submit'] == "Search":
            # The user is attempting to submit the form.  Extract the submitted
            # form data.

            err_msg = None # initially.

            data = []
            bad_data = False # initially.
            for row in range(3):
                key   = request.POST.get("key-%d" % row, "")
                value = request.POST.get("value-%d" % row, "")

                data.append({'key'   : key,
                             'value' : value})

                if ((key != "" or value != "") and
                    (key == "" or value == "")):
                    bad_data = True

            if bad_data:
                err_msg = "You must enter all information on each row."

            if err_msg == None:
                criteria = []
                for row in data:
                    if row['key'] != "" and row['value'] != "":
                        key = row['key']
                        key = key.replace("&", "%26")
                        key = key.replace("=", "%3D")
                        value = row['value']
                        value = value.replace("&", "%26")
                        value = value.replace("=", "%3D")
                        criteria.append(key + "=" + value)

                if len(criteria) == 0:
                    err_msg = "You haven't entered any data."

            if err_msg == None:
                # Redirect the user to display the matching accounts.
                return HttpResponseRedirect("/web/search_results?" +
                                            "&".join(criteria))
        elif request.POST['submit'] == "Cancel":
            return HttpResponseRedirect("/web")

    return render(request, "web/search.html", {'data'    : data,
                                               'err_msg' : err_msg})

#############################################################################

def search_results(request):
    """ Respond to the "/web/search_results" URL.

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

    page = params.get("page", 1)

    criteria = []
    for key,value in params.items():
        if key != "page":
            criteria.append([key, value])

    response = functions.search(criteria)
    if not response['success']:
        print response # Fix error handling later.
        return HttpResponseRedirect("/web")

    # Paginate the list of matching accounts, as required.

    paginator = Paginator(response['accounts'], 15)

    try:
        accounts = paginator.page(page)
    except PageNotAnInteger:
        accounts = paginator.page(1)
    except EmptyPage:
        accounts = []

    if request.method == "POST" and request.POST['submit'] == "Done":
        return HttpResponseRedirect("/web")

    return render(request, "web/view_search_results.html",
                  {'criteria'  : criteria,
                   'page'      : page,
                   'num_pages' : paginator.num_pages,
                   'accounts'  : accounts})

