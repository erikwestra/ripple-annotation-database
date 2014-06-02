""" annotationDatabase.admin.views.template

    This module implements the various template-related views for the
    annotationDatabase.admin application.
"""
import simplejson as json
import xlrd

from django.http           import HttpResponse, HttpResponseRedirect
from django.shortcuts      import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from annotationDatabase.authentication import auth_controller

from annotationDatabase.shared.models import *
from annotationDatabase.shared.lib    import backHandler

from annotationDatabase.api import functions

from annotationDatabase.admin.menus import get_admin_menus

#############################################################################

def select(request):
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

def upload(request):
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

def view(request, template_id):
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

def delete(request, template_id):
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

