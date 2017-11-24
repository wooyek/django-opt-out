# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from django.views.generic import TemplateView

from website.urls import urlpatterns

urlpatterns += [
    url(r'^mocked_goodbye/(?P<pk>[\d]+)/(?P<secret>[\w]+)/(?P<email>[^/]+)/', TemplateView.as_view(template_name='nonexistent'), name='mocked_goodbye'),
]
