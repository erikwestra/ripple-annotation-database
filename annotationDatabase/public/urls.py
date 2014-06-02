""" annotationDatabase.public.urls

    This module defines the urls for the Ripple Annotation Database's "public"
    application.
"""
from django.conf.urls import patterns, include, url

#############################################################################

urlpatterns = patterns('annotationDatabase.public.views',
    url(r'^$',                                  "main"),
    url(r'^signup$',                            "signup"),
    url(r'^accounts$',                          "accounts"),
    url(r'^accounts/add$',                      "add_account"),
    url(r'^accounts/edit/(?P<account>[^/]+)',   "edit_account"),
    url(r'^accounts/remove/(?P<account>[^/]+)', "remove_account"),
    url(r'^password$',                          "change_password"),
    url(r'^signout$',                           "signout"),
)

