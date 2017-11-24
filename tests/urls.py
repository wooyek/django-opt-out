# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, url
from django.views.generic import TemplateView

# noinspection PyUnresolvedReferences
urlpatterns = [
    url(r'^opt-out/', include('django_opt_out.urls')),
    url(r'^opt-out/', include('django_opt_out.plugins.sparkpost.urls')),
    url(r'^mocked_goodbye/(?P<pk>[\d]+)/(?P<secret>[\w]+)/(?P<email>[^/]+)/', TemplateView.as_view(template_name='nonexistent'), name='mocked_goodbye'),
]
