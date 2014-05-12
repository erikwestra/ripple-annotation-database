""" annotationDatabase.admin.views

    This module defines the various view functions for the Ripple Annotation
    Database's "admin" application.
"""
import datetime
import uuid

import simplejson as json
import xlrd

from django.http           import HttpResponse, HttpResponseRedirect
from django.shortcuts      import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from annotationDatabase.authentication import auth_controller

from annotationDatabase.shared.models import *

from annotationDatabase.api import functions

#############################################################################

def main(request):
    """ Respond to our top-level "/admin" URL.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    options = []
    options.append(["Add Annotations",            "/admin/add"])
    options.append(["Upload Annotations",         "/admin/upload"])
    options.append(["View Annotation Batches",    "/admin/select_batch"])
    options.append(["View Account Annotations",   "/admin/select_account"])
    options.append(["Search",                     "/admin/search"])
    options.append(["--------------", None])
    options.append(["View Annotation Templates",  "/admin/templates"])
    options.append(["Upload Annotation Template", "/admin/templates/upload"])
    options.append(["--------------", None])
    if auth_controller.is_admin(request):
        options.append(["Add/Edit Users",
                        auth_controller.get_user_admin_url()])
    options.append(["Add/Edit Client Systems", "/admin/clients"])

    options.append(["Change Password",
                    auth_controller.get_change_password_url()])
    options.append(["Log Out", auth_controller.get_logout_url()])

    return render(request, "admin/main.html", {'options' : options})

#############################################################################

def add(request):
    """ Respond to the "/admin/add" URL.

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
                    return HttpResponseRedirect("/admin")
                else:
                    err_msg = response['error']
        elif request.POST['submit'] == "Cancel":
            return HttpResponseRedirect("/admin")

    return render(request, "admin/add_annotations.html",
                  {'data'    : data,
                   'err_msg' : err_msg})

#############################################################################

def upload(request):
    """ Respond to the "/admin/upload" URL.

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
            return HttpResponseRedirect("/admin")

    return render(request, "admin/upload_batch.html", {'err_msg' : err_msg})

#############################################################################

def select_batch(request):
    """ Respond to the "/admin/select_batch" URL.

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
        return HttpResponseRedirect("/admin")

    batches   = response['batches']
    num_pages = response['num_pages']

    for batch in batches:
        timestamp = batch['timestamp']
        batch['timestamp'] = datetime.datetime.utcfromtimestamp(timestamp)

    if request.method == "POST" and request.POST['submit'] == "Done":
        return HttpResponseRedirect("/admin")

    return render(request, "admin/select_batch.html",
                  {'page'      : page,
                   'num_pages' : num_pages,
                   'batches'   : batches})

#############################################################################

def view_batch(request, batch_number):
    """ Respond to the "/admin/view_batch/{batch_number}" URL.

        We display the contents of the given annotation batch, and let the user
        hide annotations within the batch.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    response = functions.get(batch_number)

    if not response['success']:
        print response # Fix error handling later.
        return HttpResponseRedirect("/admin")

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
                return HttpResponseRedirect("/admin/view_batch/%s" %
                                            batch_number)

        if request.POST.get("submit") == "Done":
            return HttpResponseRedirect("/admin")

    return render(request, "admin/view_batch.html",
                  {'annotations' : annotations})

#############################################################################

def select_account(request):
    """ Respond to the "/admin/select_account" URL.

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
        return HttpResponseRedirect("/admin")

    accounts  = response['accounts']
    num_pages = response['num_pages']

    if request.method == "POST" and request.POST['submit'] == "Done":
        return HttpResponseRedirect("/admin")

    return render(request, "admin/select_account.html",
                  {'page'      : page,
                   'num_pages' : num_pages,
                   'accounts'  : accounts})

#############################################################################

def view_account(request, account):
    """ Respond to the "/admin/view_account/{account}" URL.

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
        return HttpResponseRedirect("/admin")

    paginator = Paginator(response['annotations'], 20)

    try:
        annotations = paginator.page(page)
    except PageNotAnInteger:
        annotations = paginator.page(1)
    except EmptyPage:
        annotations = []

    if request.method == "POST" and request.POST['submit'] == "Done":
        return HttpResponseRedirect("/admin/select_account")

    return render(request, "admin/view_account.html",
                  {'account'     : account,
                   'page'        : page,
                   'num_pages'   : paginator.num_pages,
                   'annotations' : annotations})

#############################################################################

def view_account_history(request, account):
    """ Respond to the "/admin/view_account/{account}" URL.

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
        return HttpResponseRedirect("/admin")

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
        return HttpResponseRedirect("/admin/select_account")

    return render(request, "admin/view_account_history.html",
                  {'account'   : account,
                   'page'      : page,
                   'num_pages' : paginator.num_pages,
                   'history'   : history})

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
                return HttpResponseRedirect("/admin/search_results?" +
                                            "&".join(criteria))
        elif request.POST['submit'] == "Cancel":
            return HttpResponseRedirect("/admin")

    return render(request, "admin/search.html", {'data'    : data,
                                                 'err_msg' : err_msg})

#############################################################################

def search_results(request):
    """ Respond to the "/admin/search_results" URL.

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
        return HttpResponseRedirect("/admin")

    # Paginate the list of matching accounts, as required.

    paginator = Paginator(response['accounts'], 15)

    try:
        accounts = paginator.page(page)
    except PageNotAnInteger:
        accounts = paginator.page(1)
    except EmptyPage:
        accounts = []

    if request.method == "POST" and request.POST['submit'] == "Done":
        return HttpResponseRedirect("/admin")

    return render(request, "admin/view_search_results.html",
                  {'criteria'  : criteria,
                   'page'      : page,
                   'num_pages' : paginator.num_pages,
                   'accounts'  : accounts})

#############################################################################

def view_clients(request):
    """ Respond to the "/admin/clients" URL.
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

    all_clients = Client.objects.all().order_by("name")

    paginator = Paginator(all_clients, 20)

    try:
        clients = paginator.page(page)
    except PageNotAnInteger:
        clients = paginator.page(1)
    except EmptyPage:
        clients = []

    if request.method == "POST":
        if request.POST['submit'] == "Done":
            return HttpResponseRedirect("/admin")
        elif request.POST['submit'] == "Add":
            return HttpResponseRedirect("/admin/clients/add")

    return render(request, "admin/view_clients.html",
                  {'page'      : page,
                   'num_pages' : paginator.num_pages,
                   'clients'   : clients})

#############################################################################

def add_client(request):
    """ Respond to the "/admin/clients/add" URL.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    if request.method == "GET":
        # This is the first time we've displayed this page -> prepare our CGI
        # parameters.
        name    = ""
        err_msg = None
    elif request.method == "POST":
        if request.POST['submit'] == "OK":
            # The user is attempting to submit the form -> extract our CGI
            # parameters and create the new client.

            err_msg = None # initially.

            name = request.POST.get("name")
            if name in ["", None]:
                err_msg = "You must enter a name for this client."

            if err_msg == None:
                try:
                    existing_client = Client.objects.get(name=name)
                except Client.DoesNotExist:
                    existing_client = None

                if existing_client != None:
                    err_msg = "There is already a client with that name."

            if err_msg == None:
                # The entered data is acceptable -> create the new client.
                client = Client()
                client.name       = name
                client.auth_token = uuid.uuid4().hex
                client.save()

                # Return the caller back to the "list clients" view.

                return HttpResponseRedirect("/admin/clients")
        elif request.POST['submit'] == "Cancel":
            return HttpResponseRedirect("/admin/clients")

    # If we get here, we're going to display the "Add Client" page.  Do so.

    return render(request, "admin/edit_client.html",
                  {'heading' : "Add Client System",
                   'name'    : name,
                   'err_msg' : err_msg})

#############################################################################

def edit_client(request, client_id):
    """ Respond to the "/admin/clients/edit/XXX" URL.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        return HttpResponseRedirect("/admin/clients") # Should never happen.

    if request.method == "GET":
        # This is the first time we've displayed this page -> prepare our CGI
        # parameters.
        name    = client.name
        err_msg = None
    elif request.method == "POST":
        if request.POST['submit'] == "OK":
            # The user is attempting to submit the form -> extract our CGI
            # parameters and create the new client.

            err_msg = None # initially.

            name = request.POST.get("name")
            if name in ["", None]:
                err_msg = "You must enter a name for this client."

            if err_msg == None:
                try:
                    existing_client = Client.objects.get(name=name)
                except Client.DoesNotExist:
                    existing_client = None

                if existing_client != None and existing_client != client:
                    err_msg = "There is already another client with that name."

            if err_msg == None:
                # The entered data is acceptable -> update the new client.
                client.name = name
                client.save()

                # Return the caller back to the "list clients" view.

                return HttpResponseRedirect("/admin/clients")
        elif request.POST['submit'] == "Cancel":
            return HttpResponseRedirect("/admin/clients")

    # If we get here, we're going to display the "Edit Client" page.  Do so.

    return render(request, "admin/edit_client.html",
                  {'heading' : "Edit Client System",
                   'name'    : name,
                   'err_msg' : err_msg})

#############################################################################

def delete_client(request, client_id):
    """ Respond to the "/admin/clients/delete/XXX" URL.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        return HttpResponseRedirect("/admin/clients") # Should never happen.

    if request.method == "POST":
        if request.POST['submit'] == "Delete":
            # The user confirmed -> delete the client.
            client.delete()

        return HttpResponseRedirect("/admin/clients")

    # Display the confirmation dialog.

    return render(request, "admin/confirm.html",
                  {'heading'  : "Delete Client System",
                   'message'  : 'Are you sure you want to delete the "' +
                                client.name + '" client?',
                   'btn_name' : "Delete"})

#############################################################################

def select_template(request):
    """ Respond to the "/admin/templates" URL.
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

    response = functions.list_templates(params.get("page"), rpp=20)
    if not response['success']:
        print response # Fix error handling later.
        return HttpResponseRedirect("/admin")

    templates = response['templates']
    num_pages = response['num_pages']

    if request.method == "POST" and request.POST['submit'] == "Done":
        return HttpResponseRedirect("/admin")

    return render(request, "admin/select_template.html",
                  {'page'      : page,
                   'num_pages' : num_pages,
                   'templates' : templates})

#############################################################################

def upload_template(request):
    """ Respond to the "/admin/templates/upload" URL.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    if request.method == "GET":
        # We're displaying this page for the first time -> prepare our CGI
        # parameters.
        template_name = ""
        err_msg       = None
    elif request.method == "POST":
        if request.POST['submit'] == "Cancel":
            # The user cancelled -> return back to the main view.
            return HttpResponseRedirect("/admin")

        # If we get here, the user is submitting the form.  Try extracting the
        # template name and the uploaded file.

        err_msg = None # initially.

        template_name = request.POST.get("name")
        if template_name in ["", None]:
            err_msg = "Please enter a name for this annotation template."

        if err_msg == None:
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

        if err_msg == None:
            if sheet.ncols < 4:
                err_msg = "That spreadsheet doesn't have enough data."

        def _get_text(cell):
            """ Extract the text from the given cell.

                Returns an empty string if the cell is empty.
            """
            if cell.ctype == xlrd.XL_CELL_EMPTY:
                return ""
            else:
                return str(cell.value)

        if err_msg == None:
            # Extract the annotation template entries from the spreadsheet.

            entries = [] # List of annotation template entries.  Each list item
                         # is a dictionary with 'annotation', 'label', 'type',
                         # 'default' entries, and possibly 'choices',
                         # 'field_size', 'field_required', 'field_min_length'
                         # and 'field_max_length' entries, as appropriate.

            for row in range(1, sheet.nrows):
                annotation = _get_text(sheet.cell(row, 0))
                label      = _get_text(sheet.cell(row, 1))
                type       = _get_text(sheet.cell(row, 2))
                default    = _get_text(sheet.cell(row, 3))

                if annotation == "":
                    err_msg = "Missing annotation key in row %d" % (row+1)
                    break

                if label == "":
                    err_msg = "Missing annotation label in row %d" % (row+1)
                    break

                if type not in ["choice", "field"]:
                    err_msg = "Invalid annotation type in row %d" % (row+1)
                    break

                if type == "choice":
                    choices = []

                    col = 4
                    while col < sheet.ncols:
                        text = _get_text(sheet.cell(row, col))
                        if text != "":
                            if "=" not in text:
                                err_msg = "Invalid choice in row %d" % (row+1)
                                break

                            key,value = text.split("=", 1)
                            key   = key.strip()
                            value = value.strip()

                            choices.append([key, value])
                        col = col + 1

                    if len(choices) == 0:
                        err_msg = "Missing choices in row %d" % (row+1)
                        break
                elif type == "field":
                    options = {}

                    col = 4
                    while col < sheet.ncols:
                        text = _get_text(sheet.cell(row, col))
                        if text != "":
                            if "=" not in text:
                                err_msg = "Invalid option in row %d" % (row+1)
                                break

                            key,value = text.split("=", 1)
                            key   = key.strip()
                            value = value.strip()

                            if key == "size":
                                try:
                                    options['field_size'] = int(value)
                                except ValueError:
                                    err_msg = ("Invalid field size in row %d" %
                                               (row+1))
                                    break
                            elif key == "required":
                                if value in ["Y", "y"]:
                                    options['field_required'] = True
                                else:
                                    options['field_required'] = False
                            elif key == "min_length":
                                try:
                                    options['field_min_length'] = int(value)
                                except ValueError:
                                    err_msg = ("Invalid min_length in row %d" %
                                               (row+1))
                                    break
                            elif key == "max_length":
                                try:
                                    options['field_max_length'] = int(value)
                                except ValueError:
                                    err_msg = ("Invalid max_length in row %d" %
                                               (row+1))
                                    break

                        if err_msg != None:
                            break

                        col = col + 1

                if err_msg != None:
                    break

                entry = {}
                entry['annotation'] = annotation
                entry['label']      = label
                entry['type']       = type
                entry['default']    = default

                if type == "choice":
                    entry['choices'] = choices
                elif type == "field":
                    entry.update(options)

                entries.append(entry)

        if err_msg == None:
            # Save the template into the database.

            response = functions.set_template(template_name, entries)

            if not response['success']:
                err_msg = response['error']

        if err_msg == None:
            return HttpResponseRedirect("/admin")

    return render(request, "admin/upload_template.html",
                  {'name'    : template_name,
                   'err_msg' : err_msg})

#############################################################################

def view_template(request, template_id):
    """ Respond to the "/admin/templates/view/XXX" URL.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    try:
        template = AnnotationTemplate.objects.get(id=template_id)
    except AnnotationTemplate.DoesNotExist:
        return HttpResponseRedirect("/admin/templates") # Should never happen.

    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponse("Bad HTTP Method")

    page = int(params.get("page", "1"))

    all_entries = [] # List of entries to display.  Each list item is a
                     # dictionary with "annotation", "label", "type", "default"
                     # and "extra" entries.  Note that the "extra" entry is a
                     # list of strings to display for the various field
                     # options or choices, as appropriate.

    template_entries = AnnotationTemplateEntry.objects.all()
    template_entries = template_entries.filter(template=template)

    for template_entry in template_entries.order_by("label"):
        entry = {}
        entry['annotation'] = template_entry.annotation.key
        entry['label']      = template_entry.label
        entry['type']       = template_entry.type
        entry['default']    = template_entry.default

        if template_entry.type == "choice":
            choices = []
            for key,value in json.loads(template_entry.choices):
                choices.append("%s=%s" % (key, value))
            entry['extra'] = choices
        elif template_entry.type == "field":
            options = []
            if template_entry.field_size != None:
                options.append("size=%d" % template_entry.field_size)
            if template_entry.field_required != None:
                if template_entry.field_required:
                    options.append("required=Y")
                else:
                    options.append("required=N")
            if template_entry.field_min_length != None:
                options.append("min_length=%d" %
                               template_entry.field_min_length)
            if template_entry.field_max_length != None:
                options.append("max_length=%d" %
                               template_entry.field_max_length)
            entry['extra'] = options

        all_entries.append(entry)

    paginator = Paginator(all_entries, 20)

    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = []

    # Pad the "extra" list out so that all entries have the same number of
    # extra cells.

    max_num_extra = 0
    for entry in entries:
        num_extra = len(entry['extra'])
        if num_extra > max_num_extra:
            max_num_extra = num_extra

    for entry in entries:
        while len(entry['extra']) < max_num_extra:
            entry['extra'].append("")

    # If the user clicked on the "Done" button, return back to the main list of
    # templates.

    if request.method == "POST":
        if request.POST.get("submit") == "Done":
            return HttpResponseRedirect("/admin/templates")

    # Finally, display the admin page.

    return render(request, "admin/view_template.html",
                  {'page'        : page,
                   'num_pages'   : paginator.num_pages,
                   'template'    : template,
                   'entries'     : entries,
                   'extra_range' : range(max_num_extra)})

#############################################################################

def delete_template(request, template_id):
    """ Respond to the "/admin/templates/delete/XXX" URL.
    """
    if not auth_controller.is_logged_in(request):
        return auth_controller.redirect_to_login()

    try:
        template = AnnotationTemplate.objects.get(id=template_id)
    except AnnotationTemplate.DoesNotExist:
        return HttpResponseRedirect("/admin/templates") # Should never happen.

    if request.method == "POST":
        if request.POST['submit'] == "Delete":
            # The user confirmed -> delete the template and all its entries.
            AnnotationTemplateEntry.objects.filter(template=template).delete()
            template.delete()

        return HttpResponseRedirect("/admin/templates")

    # Display the confirmation dialog.

    return render(request, "admin/confirm.html",
                  {'heading'  : "Delete Annotation Template",
                   'message'  : 'Are you sure you want to delete the "' +
                                template.name + '" template?',
                   'btn_name' : "Delete"})

