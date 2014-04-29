""" annotationDatabase.custom_settings

    This module defines custom settings used by the Ripple Annotation Database.
    These override values defined in the main `settings.py` module, and can
    themselves be overriden by environment variables.

    Note that this file is deliberately *not* under version control.  You can
    modify this file to customise various settings without affecting the
    server's source code.
"""
DEBUG                        = True
SET_ALLOWED_HOSTS            = False
TIME_ZONE                    = 'Pacific/Auckland'
DATABASE_URL                 = "postgres://postgres:hal9000@localhost/ripple_annotations"

