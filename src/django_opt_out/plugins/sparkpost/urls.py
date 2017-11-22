# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views as v

app_name = 'django_opt_out_sparkpost'

urlpatterns = [
    url(r'^spark-post/unsubscribe-hook$', v.SparkPostUnsubscribeWebhook.as_view(), name='SparkPostUnsubscribeWebhook'),
]
