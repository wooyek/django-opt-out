# coding=utf-8
import logging

import django.dispatch

log = logging.getLogger(__name__)

opt_out_visited = django.dispatch.Signal(providing_args=["view", "request", "context"])
opt_out_submitted = django.dispatch.Signal(providing_args=["view", "request", "opt_out"])
opt_out_deleted = django.dispatch.Signal(providing_args=["view", "request", "opt_out"])

opt_out_saved = django.dispatch.Signal(providing_args=["opt_out"])


def send_signal(signal, *args, **kwargs):
    """Log eny errors returned in the signal call responses"""
    results = signal.send_robust(*args, **kwargs)
    for receiver, response in results:
        if isinstance(response, Exception):
            log.error(response, exc_info=(type(response), response, response.__traceback__))
