""" annotationDatabase.api.urls

    This module defines the urls for the Ripple Annotation Database's "api"
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

    url(r'^get/(?P<batch_number>[^/]+)',  'get'),
    url(r'^get/(?P<batch_number>[^/]+)/', 'get'),

    url(r'^accounts',  "accounts"),
    url(r'^accounts/', "accounts"),

    url(r'^account/(?P<account>[^/]+)',  'account'),
    url(r'^account/(?P<account>[^/]+)/', 'account'),

    url(r'^account_history/(?P<account>[^/]+)',  'account_history'),
    url(r'^account_history/(?P<account>[^/]+)/', 'account_history'),

    url(r'^search',  "search"),
    url(r'^search/', "search"),

    url(r'^set_template/(?P<template_name>[^/]+)',  'set_template'),
    url(r'^set_template/(?P<template_name>[^/]+)/', 'set_template'),

    url(r'^get_template/(?P<template_name>[^/]+)',  'get_template'),
    url(r'^get_template/(?P<template_name>[^/]+)/', 'get_template'),

    url(r'^public_annotations',  "public_annotations"),
    url(r'^public_annotations/', "public_annotations"),
)

