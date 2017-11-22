# coding=utf-8

import importlib

from django.utils.functional import SimpleLazyObject

backends = SimpleLazyObject(lambda: list(get_backedns()))


def get_backedns():
    from django.conf import settings
    backends = settings.OPT_OUT_BACKENDS
    for entry in backends:
        mod_path, _, cls_name = entry.rpartition('.')
        module = importlib.import_module(mod_path)
        cls = getattr(module, cls_name)
        yield cls(settings)
