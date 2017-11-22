# -*- coding: utf-8
from __future__ import absolute_import

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DjangoOptOutSparkPostConfig(AppConfig):
    name = 'django_opt_out.plugins.sparkpost'
    verbose_name = _('Messaging Opt-Outs SparkPost plugin')

    def ready(self):
        from . import hooks  # noqa F401
