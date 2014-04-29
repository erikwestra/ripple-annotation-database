""" annotationDatabase.settings

    This module contains the Django settings for the AnnotationDatabase system.
"""
import os.path
import sys

import dj_database_url

from annotationDatabase.shared.lib.settingsImporter import SettingsImporter

#############################################################################

# Calculate the absolute path to the top-level directory for this project.

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

#############################################################################

# Load our various custom settings.

import_setting = SettingsImporter(globals(),
                                  custom_settings="annotationDatabase." +
                                                  "custom_settings",
                                  env_prefix="AD_")

import_setting("DEBUG",                        True)
import_setting("SET_ALLOWED_HOSTS",            True)
import_setting("TIME_ZONE",                    "UTC")
import_setting("DATABASE_URL",                 None)
# NOTE: DATABASE_URL uses the following general format:
#           postgres://username:password@host:port/database_name
#       or for a database on the local machine:
#           postgres://username:password@localhost/database_name
import_setting("LOG_DIR",                      os.path.join(ROOT_DIR, "logs"))
import_setting("ENABLE_DEBUG_LOGGING",         False)
import_setting("LOGGING_DESTINATION",          "file")

#############################################################################

# Our various project settings:

if SET_ALLOWED_HOSTS:
    ALLOWED_HOSTS = [".3taps.com", ".3taps.net"]
else:
    ALLOWED_HOSTS = ["*"]

TEMPLATE_DEBUG = DEBUG

LANGUAGE_CODE = 'en-us'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ukw9l@yyacd5zx*)e4^vw572n1+l9cn-9ty2*&=0f@dv0&3zo&'

TEMPLATE_DEBUG = DEBUG

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Enable the "south" database migration toolkit.

    "south",

    # Add the "BoxUI" user-interface toolkit.

    "annotationDatabase.boxUI",

    # Enable the user-authentication app.

    "annotationDatabase.authentication",

    # Add our AnnotationDatabase applications.

    "annotationDatabase.shared",
    "annotationDatabase.api",
    "annotationDatabase.web",
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Enable CORS support.

    "annotationDatabase.middleware.cors.CORSMiddleware",
)

ROOT_URLCONF = 'annotationDatabase.urls'

WSGI_APPLICATION = 'annotationDatabase.wsgi.application'

STATIC_URL = '/static/'

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

# Set up our database.

if 'test' in sys.argv:
    # Use SQLite for unit tests.
    DATABASES = {'default' : {'ENGINE' : "django.db.backends.sqlite3"}}
else:
    # Use dj_database_url to extract the database settings from the
    # DATABASE_URL setting.
    DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}

# Set up logging.  We log everything to the console for now.

LOGGING = {
    'version' : 1,

    'disable_existing_loggers' : True,

    'formatters' : {
#        'verbose' : {
#            'format' : "%(levelname)s %(asctime)s %(module)s %(message)s",
#        },
        'simple' : {
            'format' : "%(levelname)s %(message)s",
        },
    },

    'handlers' : {
        'console' : {
            'level'     : "DEBUG",
            'class'     : "logging.StreamHandler",
            'formatter' : "simple",
        },
#        'file' : {
#            'level'     : "DEBUG",
#            'class'     : "logging.FileHandler",
#            'filename'  : "/path/to/file.log",
#            'formatter' : "simple",
#        },
        'null' : {
            'level' : "DEBUG",
            'class' : "django.utils.log.NullHandler",
        },
    },

    'loggers' : {
        '' : {
            'handlers' : ["console"],
            'level'     : "DEBUG",
            'propagate' : False,
        },

        'django.db.backends' : {
            'handlers'  : ["null"], # Disable query logging when DEBUG=True.
            'level'     : "DEBUG",
            'propagate' : False,
        },
    }
}

# Configure the authentication app.

AUTHENTICATION_MAIN_URL = "/web"

