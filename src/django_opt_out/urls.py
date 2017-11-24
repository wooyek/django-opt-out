# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views as v

app_name = 'django_opt_out'

urlpatterns = [
    url(r'^$', v.OptOutConfirm.as_view(), name='OptOutConfirm'),
    url(r'^success/(?P<pk>[\d]+)/(?P<secret>[\w]+)/(?P<email>[^/]+)$', v.OptOutSuccess.as_view(), name='OptOutSuccess'),
    url(r'^update/(?P<pk>[\d]+)/(?P<secret>[\w]+)/(?P<email>[^/]+)$', v.OptOutUpdate.as_view(), name='OptOutUpdate'),
    url(r'^removed$', v.OptOutRemoved.as_view(), name='OptOutRemoved'),
]
