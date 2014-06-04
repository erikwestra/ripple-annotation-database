""" authentication.app_settings

    This module defines the application-specific settings used by the
    Authentication app.  You can override these settings within your project's
    `settings.py` module if you wish.
"""
from django.conf import settings

#############################################################################

# The list of user types supported by the Authentication app:

USER_TYPES = getattr(settings, "AUTHENTICATION_USER_TYPES",
                     ("user", "administrator"))

# The user type to use for an "administrator" user:

ADMIN_USER_TYPE = getattr(settings, "AUTHENTICATION_ADMIN_USER_TYPE",
                          "administrator")

# The label to use for a "user" of the system:

USER_LABEL = getattr(settings, "AUTHENTICATION_USER_LABEL",
                     "user")

# The default type for new users:

DEFAULT_USER_TYPE = getattr(settings, "AUTHENTICATION_DEFAULT_USER_TYPE",
                            "user")

# The main URL for the application.  This is the URL to redirect the user to
# after logging in, leaving the user admin page, etc.

MAIN_URL = getattr(settings, "AUTHENTICATION_MAIN_URL",
                   "/")

# The URL to redirect back to if the user cancels a login, or logs out.

LOGGED_OUT_URL = getattr(settings, "AUTHENTICATION_LOGGED_OUT_URL",
                         "/")

# The number of seconds a session can be idle before it times out.

MAX_IDLE_TIME = getattr(settings, "AUTHENTICATION_MAX_IDLE_TIME",
                        600)

# The heading to display at the top of the "login" page:

LOGIN_HEADING = getattr(settings, "AUTHENTICATION_LOGIN_HEADING",
                        "Login")

# The shortcut icon to use for our various pages, if any.

SHORTCUT_ICON = getattr(settings, "AUTHENTICATION_SHORTCUT_ICON",
                        None)

# An icon to show next to the heading on our various pages, if any:

HEADING_ICON = getattr(settings, "AUTHENTICATION_HEADING_ICON",
                       None)

#############################################################################

# The base package for our Authentication app.  This is the "module" path used
# to import our various modules.  Note that this is calculated automatically.

APP_MODULE_PATH = ".".join(__name__.split(".")[:-1])

