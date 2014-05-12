""" annotationDatabase.public.admin.urls

    This module defines the urls for the public application's "admin" views.
    These are installed into the URL tree under "/admin/public".
"""
from django.conf.urls import patterns, include, url

#############################################################################

urlpatterns = patterns('annotationDatabase.public.admin.views',
    url(r'^users$',                                "user_admin"),
    url(r'^users/block/(?P<user_id>[^/]+)',        "block_user"),
    url(r'^users/unblock/(?P<user_id>[^/]+)',      "unblock_user"),
    url(r'^users/delete/(?P<user_id>[^/]+)',       "delete_user"),
    url(r'^accounts$',                             "account_admin"),
    url(r'^accounts/delete/(?P<account_id>[^/]+)', "delete_account"),
)

