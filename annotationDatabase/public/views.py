""" annotationDatabase.public.views

    This module defines the various view functions for the Ripple Annotation
    Database's "public" application.
"""
import datetime
import uuid

from django.http           import HttpResponse, HttpResponseRedirect
from django.shortcuts      import render
from django.utils          import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf           import settings

from annotationDatabase.shared.models import *
from annotationDatabase.api           import functions

#############################################################################

def main(request):
    """ Respond to our top-level "/public" URL.

        We let the user sign up or sign in, as appropriate.
    """
    session = get_session(request)
    if session != None:
        return HttpResponseRedirect("/public/accounts")

    if request.method == "GET":
        # This is the first time we've displayed this page -> prepare our CGI
        # parameters.

        signup_err_msg  = None
        signin_username = ""
        signin_err_msg  = None

    elif request.method == "POST":

        signup_err_msg  = None # initially.
        signin_err_msg  = None # ditto.
        signup_password = request.POST.get("signup_password", "")
        signin_username = request.POST.get("signin_username", "")
        signin_password = request.POST.get("signin_password", "")

        if signup_password != "":

            # The user is attempting to sign up.  Check the entered password.

            if signup_password != settings.PUBLIC_SIGNUP_PASSWORD:
                signup_err_msg = "Invalid password"
            else:
                return HttpResponseRedirect("/public/signup?signup_password=%s"
                                            % signup_password)

        elif signin_username != "" or signin_password != "":

            # The user is attempting to sign in.  Check the entered username
            # and password.

            try:
                user = User.objects.get(username__iexact=signin_username)
            except User.DoesNotExist:
                user = None

            if user == None or not user.is_password_correct(signin_password):
                signin_err_msg = "Invalid username or password"
            elif user.blocked:
                signin_err_msg = "You have been blocked by an administrator"
            else:
                create_session(request, user)
                return HttpResponseRedirect("/public/accounts")

    return render(request, "public/main.html",
                  {'signup_err_msg'  : signup_err_msg,
                   'signin_username' : signin_username,
                   'signin_err_msg'  : signin_err_msg})

#############################################################################

def signup(request):
    """ Respond to the "/public/signup" URL.

        We let a user sign up to the Annotation Database system.
    """
    if request.method == "GET":

        # We're displaying the page for the first time -> prepare our CGI
        # parameters.

        signup_password = request.GET.get("signup_password")
        username        = ""
        password1       = ""
        password2       = ""
        err_msg         = None

    elif request.method == "POST":

        # The user is submitting our form.  See what they want to do.

        if request.POST.get("submit") == "Cancel":
            # The user is cancelling -> return to the main page.
            return HttpResponseRedirect("/public")

        # If we get here, the user is trying to sign up.  Check the entered
        # data.

        signup_password = request.POST.get("signup_password")
        username        = request.POST.get("username")
        password1       = request.POST.get("password1")
        password2       = request.POST.get("password2")
        err_msg         = None # initially.

        if username in [None, ""]:
            err_msg = "You must enter a username."

        if err_msg == None:
            try:
                existing_user = User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                existing_user = None

            if existing_user != None:
                err_msg = "Sorry, that username is already in use."

        if err_msg == None:
            if password1 in [None, ""]:
                err_msg = "You must enter a password."

        if err_msg == None:
            if len(password1) < 5:
                err_msg = "That password is too short."

        if err_msg == None:
            if password1 != password2:
                err_msg = "The entered passwords do not match."

        if err_msg == None:
            user = User()
            user.username = username
            user.set_password(password1)
            user.save()

            create_session(request, user)
            return HttpResponseRedirect("/public/accounts")

    # If we get here, we're going to display the form.  First check that the
    # entered signup password is valid.  This ensures we're not called without
    # the signup password.

    if signup_password != settings.PUBLIC_SIGNUP_PASSWORD:
            return HttpResponseRedirect("/public")

    # Finally, display the form to the user.

    return render(request, "public/signup.html",
                  {'signup_password' : signup_password,
                   'username'        : username,
                   'password1'       : password1,
                   'password2'       : password2,
                   'err_msg'         : err_msg})

#############################################################################

def accounts(request):
    """ Respond to the "/public/accounts" URL.

        We display the user's accounts, let them add/edit/remove accounts, and
        access various options such as changing their password, signing out,
        etc.
    """
    session = get_session(request)
    if session == None:
        return HttpResponseRedirect("/public")

    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponse("Bad HTTP Method")

    page = int(params.get("page", "1"))

    all_accounts = Account.objects.filter(owner=session.user)
    paginator = Paginator(all_accounts.order_by("address"), 10)

    try:
        accounts_in_page = paginator.page(page)
    except PageNotAnInteger:
        accounts_in_page = paginator.page(1)
    except EmptyPage:
        accounts_in_page = []

    accounts = []
    for account in accounts_in_page:
        accounts.append(account.address)

    return render(request, "public/accounts.html",
                  {'menus'         : get_public_menus(request),
                   'current_url'   : "/public/accounts",
                   'username'      : get_username(request),
                   'page'          : page,
                   'num_pages'     : paginator.num_pages,
                   'accounts'      : accounts})

#############################################################################

def add_account(request):
    """ Respond to the "/public/accounts/add" URL.

        We let the user add a new account to the list of accounts owned by this
        user.
    """
    session = get_session(request)
    if session == None:
        return HttpResponseRedirect("/public")

    if request.method == "GET":

        # We're displaying the page for the first time -> prepare our CGI
        # parameters.

        address = ""
        err_msg = None

    elif request.method == "POST":

        # The user is submitting our form.  See what they want to do.

        if request.POST.get("submit") == "Cancel":
            # The user is cancelling -> return to the accounts page.
            return HttpResponseRedirect("/public/accounts")

        # If we get here, the user is trying to add an account.  Check the
        # entered data.

        address = request.POST.get("address")
        err_msg = None # initially.

        if address in [None, ""]:
            err_msg = "You must enter the desired account address."

        if err_msg == None:
            try:
                existing_account = Account.objects.get(address=address)
            except Account.DoesNotExist:
                existing_account = None

            if existing_account != None and existing_account.owner != None:
                err_msg = ("That account belongs to someone else.  " +
                           "If you think this is a mistake, please email " +
                           settings.PUBLIC_CONFLICT_EMAIL)

        if err_msg == None:
            if existing_account != None:
                existing_account.owner = session.user
                existing_account.save()
            else:
                account = Account()
                account.address = address
                account.owner   = session.user
                account.save()

            return HttpResponseRedirect("/public/accounts")

    # Finally, display the form to the user.

    return render(request, "public/add_account.html",
                  {'menus'       : get_public_menus(request),
                   'current_url' : "/public/accounts/add",
                   'address'     : address,
                   'err_msg'     : err_msg,
                  })

#############################################################################

def edit_account(request, account):
    """ Respond to the "/public/accounts/edit/XXX" URL.

        We let the user view/edit the annotations for the given account.
    """
    session = get_session(request)
    if session == None:
        return HttpResponseRedirect("/public")

    # Get the annotation template to use.

    response = functions.get_template(settings.PUBLIC_TEMPLATE_NAME)
    if not response['success']:
        return HttpResponse("Missing template '%s'" %
                            settings.PUBLIC_TEMPLATE_NAME)
    template = response['template']

    # Get the current set of annotation values for the given account.

    values = {} # Maps annotation key to current value.
    response = functions.account(account)
    if response['success']:
        for entry in response['annotations']:
            values[entry['key']] = entry['value']

    # Build the list of annotations to display.

    annotations = [] # List of annotations to display.  Each list item is a
                     # dictionary with the following entries:
                     #
                     #     'annotation'
                     #
                     #         The annotation key for this annotation.
                     #
                     #     'value'
                     #
                     #         The current value to use for this annotation.
                     #
                     #     'label'
                     #
                     #         A label to display for this annotation.
                     #
                     #     'type'
                     #
                     #          A string indicating the type of annotation
                     #          value to be entered.  The following type values
                     #          are currently supported:
                     #
                     #              "choice"
                     #
                     #                  The user can choose between two or more
                     #                  values.
                     #
                     #              "field"
                     #
                     #                  The user can enter a value directly
                     #                  into an input field.
                     #
                     #
                     #      'choices'
                     #
                     #          An array of possible values the user can choose
                     #          between. Each entry in the array will be
                     #          another array with two entries, where the first
                     #          entry is the desired annotation value, and the
                     #          second entry is the label to display to the
                     #          user when this annotation value is selected.
                     #          For example:
                     #
                     #              choices: [["M", "Male"], ["F", "Female"]]
                     #
                     #          Note that this entry will only be present for
                     #          "choice" annotations.
                     #
                     #      'field_size'
                     #
                     #          If not None, this will be the desired width of
                     #          the input field, in characters.  This
                     #          corresponds to the size attribute for an HTML
                     #          <input> tag. Note that if this is not
                     #          specified, the client will choose a default
                     #          width.
                     #
                     #      'field_required'
                     #
                     #          This will be True if the user is required to
                     #          enter a value for this annotation.  If this is
                     #          False, the annotation will not be required.
                     #
                     #      'field_min_length'
                     #
                     #          This is the minimum allowable length for this
                     #          annotation value, or None if no minimum length
                     #          is to be imposed.
                     #
                     #      'field_max_length'
                     #
                     #          This is the maximum allowable length for this
                     #          annotation value, or None if no maximum length
                     #          is to be imposed.
                     #
                     #      'err_msg'
                     #
                     #          An error message to display for this entry, or
                     #          None if no error message is to be displayed.

    for entry in template:
        annotation = {}
        annotation['annotation'] = entry['annotation']
        annotation['value']      = values.get(entry['annotation'],
                                              entry.get('default', ""))
        annotation['label']      = entry['label']
        annotation['type']       = entry['type']

        if entry['type'] == "choice":
            annotation['choices'] = entry['choices']
        elif entry['type'] == "field":
            if "field_size" in entry:
                annotation['field_size'] = entry['field_size']
            else:
                annotation['field_size'] = None

            if "field_required" in entry:
                annotation['field_required'] = entry['field_required']
            else:
                annotation['field_required'] = False

            if "field_min_length" in entry:
                annotation['field_min_length'] = entry['field_min_length']
            else:
                annotation['field_min_length'] = None

            if "field_max_length" in entry:
                annotation['field_max_length'] = entry['field_max_length']
            else:
                annotation['field_max_length'] = None

        annotations.append(annotation)

    # Prepare to show our form.

    if request.method == "GET":

        for annotation in annotations:
            annotation['err_msg'] = None

    elif request.method == "POST":

        # The user is submitting our form.  See what they want to do.

        if request.POST.get("submit") == "Cancel":
            # The user is cancelling -> return to the list of accounts.
            return HttpResponseRedirect("/public/accounts")

        # If we get here, the user is trying to save their changes.  Check
        # the entered data.

        changes   = {} # List of annotations and their updated values.
        has_error = False # initially.
        for annotation in annotations:
            err_msg = None # initially.
            value   = request.POST.get(annotation['annotation'], "")

            if annotation['type'] == "choice":

                if value != annotation['value']:
                    changes[annotation['annotation']] = value

            elif annotation['type'] == "field":

                if value == "" and annotation['field_required']:
                    has_error = True
                    err_msg   = "You must enter a value here."

                if err_msg == None:
                    if annotation['field_min_length'] != None:
                        if len(value) < annotation['field_min_length'] :
                            has_error = True
                            err_msg   = "Too short."

                if err_msg == None:
                    if annotation['field_max_length'] != None:
                        if len(value) > annotation['field_max_length'] :
                            has_error = True
                            err_msg   = "Too long."

                if err_msg == None:
                    if value != annotation['value']:
                        changes[annotation['annotation']] = value

                annotation['value'] = value

            annotation['err_msg'] = err_msg

        if not has_error:
            # No error -> save the changes into the database.

            if len(changes) > 0:
                batch = {'user_id'     : session.user.username,
                         'annotations' : []}
                for key,value in changes.items():
                    batch['annotations'].append({'account' : account,
                                                 'key'     : key,
                                                 'value'   : value})
                response = functions.add(batch)

            return HttpResponseRedirect("/public/accounts")

    # Finally, show our form to the user.

    return render(request, "public/edit_account.html",
                  {'menus'       : get_public_menus(request),
                   'current_url' : "/public/accounts/edit",
                   'account'     : account,
                   'annotations' : annotations})

#############################################################################

def remove_account(request, account):
    """ Respond to the "/public/accounts/remove/XXX" URL.

        We let the user remove the given account.
    """
    session = get_session(request)
    if session == None:
        return HttpResponseRedirect("/public")

    try:
        account = Account.objects.get(address=account)
    except Account.DoesNotExist:
        return HttpResponseRedirect("/public/accounts") # Should never happen.

    if request.method == "POST":
        if request.POST['submit'] == "Remove":
            # The user confirmed -> remove the account.
            account.delete()

        return HttpResponseRedirect("/public/accounts")

    # Display the confirmation dialog.

    return render(request, "public/remove_account.html",
                  {'menus'       : get_public_menus(request),
                   'current_url' : "/public/accounts/remove",
                   'account'     : account})

#############################################################################

def change_password(request):
    """ Respond to the "/public/password" URL.

        We let the user change their password.
    """
    session = get_session(request)
    if session == None:
        return HttpResponseRedirect("/public")

    if request.method == "GET":

        # We're displaying the page for the first time -> prepare our CGI
        # parameters.

        old_password  = ""
        new_password1 = ""
        new_password2 = ""
        err_msg       = None

    elif request.method == "POST":

        # The user is submitting our form.  See what they want to do.

        if request.POST.get("submit") == "Cancel":
            # The user is cancelling -> return to the accounts page.
            return HttpResponseRedirect("/public/accounts")

        # If we get here, the user is trying to change their password.  Check
        # the entered data.

        old_password  = request.POST.get("old_password")
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")
        err_msg       = None # initially.

        if old_password in [None, ""]:
            err_msg = "You must enter your existing password."

        if err_msg == None:
            if not session.user.is_password_correct(old_password):
                err_msg = "That is not your existing password"

        if err_msg == None:
            if new_password1 in [None, ""]:
                err_msg = "You must enter a new password."

        if err_msg == None:
            if len(new_password1) < 5:
                err_msg = "That password is too short."

        if err_msg == None:
            if new_password1 != new_password2:
                err_msg = "The entered passwords do not match."

        if err_msg == None:
            session.user.set_password(new_password1)
            session.user.save()
            return HttpResponseRedirect("/public/accounts")

    # Finally, display the form to the user.

    return render(request, "public/change_password.html",
                  {'menus'           : get_public_menus(request),
                   'current_url'     : "/public/accounts/remove",
                   'old_password'    : old_password,
                   'new_password1'   : new_password1,
                   'new_password2'   : new_password2,
                   'err_msg'         : err_msg})

#############################################################################

def signout(request):
    """ Respond to the "/public/signout" URL.

        We sign the user out.
    """
    session = get_session(request)
    if session == None:
        return HttpResponseRedirect("/public")

    delete_session(request)
    return HttpResponseRedirect("/public")

#############################################################################

def select_public(request):
    """ Respond to the "/public/public_annotations" URL.

        We let the user choose which public annotation to display.
    """
    session = get_session(request)
    if session != None:
        return HttpResponseRedirect("/public/accounts")

    response = functions.get_template(settings.PUBLIC_TEMPLATE_NAME)
    if not response['success']:
        return HttpResponse("Internal error:" + response['error'])

    public_annotations = [] # List of available annotation.  Each list item is
                            # a (label, key) tuple.

    for annotation in response['template']:
        if annotation['public']:
            public_annotations.append((annotation['label'],
                                       annotation['annotation']))

    public_annotations.sort()

    return render(request, "public/select_public.html",
                  {'public_annotations' : public_annotations})

#############################################################################

def view_public(request, annotation):
    """ Respond to the "/public/public_annotations/XXX" URL.

        We display the set of accounts with the given annotation key.
    """
    session = get_session(request)
    if session != None:
        return HttpResponseRedirect("/public/accounts")

    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponse("Bad HTTP Method")

    page = int(params.get("page", "1"))

    response = functions.public_annotations(annotation, page=page, rpp=20)
    if not response['success']:
        return HttpResponse("Internal error:" + response['error'])

    num_pages = response['num_pages']
    accounts  = response['accounts']

    response = functions.get_template(settings.PUBLIC_TEMPLATE_NAME)
    if not response['success']:
        return HttpResponse("Internal error:" + response['error'])

    annotation_label = None
    for entry in response['template']:
        if annotation == entry['annotation']:
            annotation_label = entry['label']

    return render(request, "public/view_public.html",
                  {'annotation' : annotation_label,
                   'page'       : page,
                   'num_pages'  : num_pages,
                   'accounts'   : accounts})

"""

    Public Annotations

        [previous]    Viewing page 1 of 1   [next]

        Account Address      XXXXXXX
        ---------------      -------
        r123...              Y
        r345..               Y
        r234...              N

        <Done>
"""

#############################################################################
#                                                                           #
#                    P R I V A T E   D E F I N I T I O N S                  #
#                                                                           #
#############################################################################

def get_session(request):
    """ Return the Session object associated with the given HttpRequest.

        We update the Session's last_access time so that we remember when the
        session was last accessed.

        If there is no valid session for this request, we return None.
    """
    session_token = request.session.get("public_session_token")
    if session_token == None:
        return None

    try:
        session = Session.objects.get(session_token=session_token)
    except Session.DoesNotExist:
        return None

    now = timezone.now()
    age = now - session.last_access
    if age > datetime.timedelta(seconds=600):
        # Session timed out -> delete it.
        session.delete()
        return None

    session.last_access = now
    session.save()

    return session

#############################################################################

def get_username(request):
    """ Return the username of the currently logged-in user.

        We return the username of the user associated with the given
        HttpRequest.  If there is no user currently logged in, we return None.
    """
    session = get_session(request)
    if session == None:
        return None
    else:
        return session.user.username
        
#############################################################################

def create_session(request, user):
    """ Create a new Session object for the given user and HttpRequest.
    """
    session_token = uuid.uuid4().hex

    session = Session()
    session.session_token = session_token
    session.user          = user
    session.last_access   = timezone.now()
    session.save()

    request.session['public_session_token'] = session_token

#############################################################################

def delete_session(request):
    """ Delete the Session object associated with the given HttpRequest.
    """
    session = get_session(request)
    if session != None:
        session.delete()
    del request.session['public_session_token']

#############################################################################

def get_public_menus(request):
    """ Return the menus to display at the top of our page.

        The returned value should be passed to a Django template in a template
        variable named 'menus'.  If this template is based on shared/base.html,
        the menus will be created automatically.
    """
    username_menu_items = [
        ("Change Password", "/public/password"),
        ("Sign Out",        "/public/signout"),
    ]

    username = get_username(request)
    if username == None:
        username = "User"

    menus = []
    menus.append({'title' : username,
                  'items' : username_menu_items})

    return menus

