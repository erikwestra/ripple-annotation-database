""" annotationDatabase.web.urls

    This module defines the urls for the Ripple Annotation Database's "web"
    application.
"""
from django.conf.urls import patterns, include, url

#############################################################################

urlpatterns = patterns('annotationDatabase.web.views',
    url(r'^$',                                       "main"),
    url(r'^add$',                                    "add"),
    url(r'^upload$',                                 "upload"),
    url(r'^select_batch$',                           "select_batch"),
    url(r'^view_batch/(?P<batch_number>[^/]+)',      "view_batch"),
    url(r'^select_account$',                         "select_account"),
    url(r'^view_account/(?P<account>[^/]+)',         "view_account"),
    url(r'^view_account_history/(?P<account>[^/]+)', "view_account_history"),
    url(r'^search$',                                 "search"),
    url(r'^search_results$',                         "search_results"),
    url(r'^clients$',                                "view_clients"),
    url(r'^clients/add$',                            "add_client"),
    url(r'^clients/edit/(?P<client_id>[^/]+)',       "edit_client"),
    url(r'^clients/delete/(?P<client_id>[^/]+)',     "delete_client"),
    url(r'^templates$',                              "select_template"),
    url(r'^templates/upload$',                       "upload_template"),
    url(r'^templates/view/(?P<template_id>[^/]+)',   "view_template"),
    url(r'^templates/delete/(?P<template_id>[^/]+)', "delete_template"),
)

