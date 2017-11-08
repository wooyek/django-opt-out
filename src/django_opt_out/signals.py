# coding=utf-8

import django.dispatch

opt_out_visited = django.dispatch.Signal(providing_args=["view", "request", "context"])
opt_out_submitted = django.dispatch.Signal(providing_args=["view", "request", "opt_out"])
