""" annotationDatabase.admin.views.client

    This module defines the various client-related views for the
    annotationDatabase.admin application.
"""
import uuid

from django.http           import HttpResponse, HttpResponseRedirect
from django.shortcuts      import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from annotationDatabase.authentication import auth_controller

from annotationDatabase.shared.models import *
from annotationDatabase.shared.lib    import backHandler

from annotationDatabase.admin.menus import get_admin_menus

#############################################################################

def view(request):
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

def add(request):
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

def edit(request, client_id):
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

def delete(request, client_id):
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

