About the Authentication App
----------------------------

The "Authentication" app is a reusable Django application that provides user
authentication for any project.  It handles the creation of various types of
users, user login and logout, and session authentication.

Note that this app does not depend on the built-in Django "auth" module;
Authentication users are completely separate from Django users.


Using Authentication
--------------------

In addition to maintaining a list of users, the Authentication app provides the
following functionality:

 * The ability to associate a user with the current session, to check the
   user's login status, and to retrieve the details of the currently logged-in
   user when needed.

 * A "login" view function to log the user in.

 * A "logout" view function to log the user out.

 * A "change password" view function to let a user change their password.

 * A "user admin" view function that allows an administrator to add, edit and
   delete other users.

 
Dependencies
------------

The Authentication app requires the "boxUI" application to be installed.  Make
sure that "boxUI" is in the list of INSTALLED_APPS before using the
Authentication app.


App-Specific Settings
---------------------

The Authentication app uses a number of settings, defined in the `app_settings`
module, which you can overwrite in your own `settings.py` module to customise
the way the Authentication module works.


Adding Authentication to your Project
-------------------------------------

To make use of the Authentication app, simply include the app's directory
somewhere in your Django project.  The Authentication app does not require that
it sits at the top level; you can place it in a sub-package if you prefer.

After adding the Authentication app to your list of INSTALLED_APPS, you will
need to import the `authentication.urls` module from within your project's
`urls.py` module.  For example:

    urlpatterns += patterns('',
        url(r'^/user/', include('authentication.urls')),
    )

You will also need to define various "AUTHENTICATION_" settings in your
`settings.py` module so that the Authentication app works the way you want it
to.  See the `app_settings.py` module for details.

Because the Authentication app requires Django sessions, make sure you include
"django.conrib.sessions.middleware.SessionMiddleware" in your
MIDDLEWARE_CLASSES setting, and "django.contrib.sessions" in your INSTALL_APPS
setting.  You may also want to enable cookie-based sessions, by setting
SESSION_ENGINE to "django.contrib.sessions.backends.signed_cookies".

One all this is done, you can make use of the `auth_controller` module to
control access to various parts of your system.  For example, in a view
function you might want to ensure that the user is logged in:

    def my_view(request):
        """ My view function.
        """
        if not auth_controller.is_logged_in(request):
            return auth_controller.redirect_to_login())
        ...


Initial Setup
-------------

To use the Authentication system for the first time, you need to have at least
one "administrator" user set up.  To do this, use the "create_admin_user"
management command, like this:

    python manage.py create_admin_user <username>

You will be prompted to enter the user's password.

Once this has been done, you can log in to the project as this user, and use
the Authentication app's user-editing logic to add more regular users.

