# coding=utf-8
from email.utils import parseaddr

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import resolve_url
from six.moves.urllib.parse import urlencode


def get_opt_out_url(email, base_url=None, *tags):
    base_url = base_url or settings.OPT_OUT_BASE_URL or ''
    return base_url + get_opt_out_path(email=email, *tags)


def get_opt_out_path(email, *tags):
    password = get_password(email)
    name, email = parseaddr(email)
    query = [('email', email), ('tag', tags)]
    if settings.OUT_OUT_REQUIRE_CONFIRMATION:
        query.append(('auth', password))
    query = urlencode(query, doseq=True)
    url = resolve_url("django_opt_out:OptOutConfirm")
    return "?".join((url, query))


def get_password(email):
    password = settings.OPT_OUT_SECRET + email
    return make_password(password, hasher=settings.OPT_OUT_PASSWORD_HASHER)


def validate_password(email, encoded):
    password = settings.OPT_OUT_SECRET + email
    return check_password(password, encoded)
