""" annotationDatabase.admin.urls

    This module defines the urls for the Ripple Annotation Database's "admin"
    application.
"""
from django.conf.urls import patterns, include, url

#############################################################################

urlpatterns = patterns('annotationDatabase.admin.views',
    url(r'^$',                                        "user.list"),
    url(r'^users/(?P<user_id>[^/]+)/accounts$',       "user.accounts"),
    url(r'^users/(?P<user_id>[^/]+)/block$',          "user.block"),
    url(r'^users/(?P<user_id>[^/]+)/unblock$',        "user.unblock"),
    url(r'^users/(?P<user_id>[^/]+)/delete$',         "user.delete"),
    url(r'^users/(?P<user_id>[^/]+)/remove/(?P<account>[^/]+)$',
                                                      "user.remove_account"),

    url(r'^accounts/(?P<account>[^/]+)/current$',     "account.view_current"),
    url(r'^accounts/(?P<account>[^/]+)/history$',     "account.view_history"),

    url(r'^annotations/add$',                         "annotation.add"),
    url(r'^annotations/upload$',                      "annotation.upload"),
    url(r'^annotations/account$',                   "annotation.select_account"),
    url(r'^annotations/batch$',                       "annotation.select_batch"),
    url(r'^annotations/batch/(?P<batch_number>[^/]+)',"annotation.view_batch"),
    url(r'^annotations/hide/(?P<batch_number>[^/]+)', "annotation.hide"),

    url(r'^search$',                                  "search.search"),
    url(r'^search/results$',                          "search.search_results"),

    url(r'^clients$',                                 "client.list"),
    url(r'^clients/add$',                             "client.add"),
    url(r'^clients/edit/(?P<client_id>[^/]+)',        "client.edit"),
    url(r'^clients/delete/(?P<client_id>[^/]+)',      "client.delete"),

    url(r'^templates$',                               "template.list"),
    url(r'^templates/upload$',                        "template.upload"),
    url(r'^templates/view/(?P<template_id>[^/]+)',    "template.view"),
    url(r'^templates/delete/(?P<template_id>[^/]+)',  "template.delete"),
)

