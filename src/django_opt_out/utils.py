# coding=utf-8
from urllib.parse import urlencode
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password


def get_opt_out_url(email, *tags, base_url=None):
    from django.shortcuts import resolve_url
    password = get_password(email)
    query = [('email', email), ('tag', tags)]
    if settings.OUT_OUT_REQUIRE_CONFIRMATION:
        query.append(('auth', password))
    query = urlencode(query, doseq=True)
    base_url = base_url or settings.OPT_OUT_BASE_URL or ''
    url = base_url + resolve_url("django_opt_out:OptOutConfirm")
    return "?".join((url, query))


def get_password(email):
    password = settings.OPT_OUT_SECRET + email
    return make_password(password, hasher=settings.OPT_OUT_PASSWORD_HASHER)


def validate_password(email, encoded):
    password = settings.OPT_OUT_SECRET + email
    return check_password(password, encoded)
