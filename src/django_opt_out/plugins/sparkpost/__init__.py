# coding=utf-8
import sparkpost
from django.conf import settings
from django.utils.functional import SimpleLazyObject


def get_client(setting='SPARKPOST_API_KEY'):
    return sparkpost.SparkPost(getattr(settings, setting, None))


client = SimpleLazyObject(get_client)
