""" authentication.urls

    This module defines the URLs for the Authentication app.
"""
from django.conf.urls import *

import app_settings

#############################################################################

# Define our URLs relative to that path.

urlpatterns = patterns(app_settings.APP_MODULE_PATH + ".views",
    url('^login$',                                 'login.login'),
    url('^logout$',                                'logout.logout'),
    url('^password$',                              'password.password'),
    url('^admin$',                                 'admin.main'),
    url('^admin/add_user$',                        'admin.add_user'),
    url('^admin/edit_user$',                       'admin.edit_user'),
    url('^admin/edit_user/(?P<user_id>(\d+))/$',   'admin.edit_user'),
    url('^admin/delete_user$',                     'admin.delete_user'),
    url('^admin/delete_user/(?P<user_id>(\d+))/$', 'admin.delete_user'),
)
