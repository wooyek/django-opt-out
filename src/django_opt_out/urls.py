# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views as v

app_name = 'django_opt_out'

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="django_opt_out/base.html")),
    url(r'^opt-out$', v.OptOutConfirm.as_view(), name='OptOutConfirm'),
    url(r'^opt-out/(?P<pk>[\d]+)/(?P<secret>[\w]+)/(?P<email>[^/]+)$', v.OptOutSuccess.as_view(), name='OptOutSuccess'),
    url(r'^opt-out/(?P<pk>[\d]+)/(?P<secret>[\w]+)/(?P<email>[^/]+)/update$', v.OptOutUpdate.as_view(), name='OptOutUpdate'),
]
