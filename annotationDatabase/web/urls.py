""" annotationDatabase.web.urls

    This module defines the urls for the Ripple Annotation Database's "web"
    application.
"""
from django.conf.urls import patterns, include, url

#############################################################################

urlpatterns = patterns('annotationDatabase.web.views',
    url(r'^$',                                       "main"),
    url(r'^add$',                                    "add"),
    url(r'^upload$',                                 "upload"), # TBD.
    url(r'^select_batch$',                           "select_batch"),
    url(r'^view_batch/(?P<batch_number>[^/]+)',      "view_batch"),
    url(r'^select_account$',                         "select_account"),
    url(r'^view_account/(?P<account>[^/]+)',         "view_account"),
    url(r'^view_account_history/(?P<account>[^/]+)', "view_account_history"),
    url(r'^search$',                                 "search"),
    url(r'^search_results$',                         "search_results"),
)

