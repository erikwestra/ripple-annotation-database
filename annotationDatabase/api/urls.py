""" annotationDatabase.web.urls

    This module defines the urls for the Ripple Annotation Database's "web"
    application.
"""
from django.conf.urls import patterns, include, url

#############################################################################

urlpatterns = patterns('annotationDatabase.api.views',
    url(r'^add',  "add"),
    url(r'^add/', "add"),

    url(r'^hide',  "hide"),
    url(r'^hide/', "hide"),

    url(r'^list',  "list"),
    url(r'^list/', "list"),

    url('^get/(?P<batch_number>[^/]+)',  'get'),
    url('^get/(?P<batch_number>[^/]+)/', 'get'),

    url(r'^accounts',  "accounts"),
    url(r'^accounts/', "accounts"),

    url('^account/(?P<account>[^/]+)',  'account'),
    url('^account/(?P<account>[^/]+)/', 'account'),

    url('^account_history/(?P<account>[^/]+)',  'account_history'),
    url('^account_history/(?P<account>[^/]+)/', 'account_history'),

    url(r'^search',  "search"),
    url(r'^search/', "search"),

    url('^set_template/(?P<template_name>[^/]+)',  'set_template'),
    url('^set_template/(?P<template_name>[^/]+)/', 'set_template'),

    url('^get_template/(?P<template_name>[^/]+)',  'get_template'),
    url('^get_template/(?P<template_name>[^/]+)/', 'get_template'),
)

