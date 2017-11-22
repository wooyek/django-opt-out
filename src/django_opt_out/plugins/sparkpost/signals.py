# coding=utf-8

import django.dispatch

list_unsubscribe = django.dispatch.Signal(providing_args=['request', 'email', 'data'])
link_unsubscribe = django.dispatch.Signal(providing_args=['request', 'email', 'data'])
