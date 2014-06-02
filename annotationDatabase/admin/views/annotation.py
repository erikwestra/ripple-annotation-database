""" annotationDatabase.admin.views.annotation

    This module defines the various annoation-related view functions for the
    annotationDatabase.admin application.
"""
import datetime

import xlrd

from django.http           import HttpResponse, HttpResponseRedirect
from django.shortcuts      import render

from annotationDatabase.authentication import auth_controller

from annotationDatabase.shared.models import *

from annotationDatabase.api import functions

from annotationDatabase.admin.menus import get_admin_menus

#############################################################################

def add(request):
    """ Respond to the "/admin/annotations/add" URL.

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
    """ Respond to the "/admin/annotations/upload" URL.

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
    """ Respond to the "/admin/annotations/view" URL.

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
    """ Respond to the "/admin/annotations/view/{batch_number}" URL.

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

