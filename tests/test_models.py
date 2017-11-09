#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-opt-out
------------

Tests for `django-opt-out` models module.
"""
from django.test import SimpleTestCase, TestCase
from django.test.utils import override_settings
from mock import patch

from six.moves.urllib.parse import quote_plus

from django_opt_out import factories, models
from django_opt_out.utils import get_opt_out_url, get_password, validate_password


@override_settings(OUT_OUT_REQUIRE_CONFIRMATION=False)
class TestOptOutUrl(SimpleTestCase):
    def test_no_tags(self):
        url = get_opt_out_url('foo@bar.com')
        self.assertEqual(url, '/opt-out?email=foo%40bar.com')

    def test_one_tag(self):
        url = get_opt_out_url('foo2@bar.com', 'notification')
        self.assertEqual(url, '/opt-out?email=foo2%40bar.com&tag=notification')

    def test_multiple_tags(self):
        url = get_opt_out_url('foo@bar.com', 'notifications', 'comments')
        self.assertEqual(url, '/opt-out?email=foo%40bar.com&tag=notifications&tag=comments')

    def test_many_tags(self):
        url = get_opt_out_url('foo@bar.com', 'notifications', 'comments')
        self.assertEqual(url, '/opt-out?email=foo%40bar.com&tag=notifications&tag=comments')

    def test_tags_values(self):
        url = get_opt_out_url('foo@bar.com', 'notifications:123', 'comments:owner')
        self.assertEqual(url, '/opt-out?email=foo%40bar.com&tag=notifications%3A123&tag=comments%3Aowner')

    @override_settings(OPT_OUT_BASE_URL='https://ex.com')
    def test_settings_base_url(self):
        url = get_opt_out_url('foo@bar.com', )
        self.assertEqual(url, 'https://ex.com/opt-out?email=foo%40bar.com')

    @override_settings(OUT_OUT_REQUIRE_CONFIRMATION=True)
    @patch('django.contrib.auth.hashers.BasePasswordHasher.salt')
    def test_password_in_url(self, salt):
        salt.return_value = 'salty'
        opt_out = get_opt_out_url('foo@bar.com', base_url='http://by.com')
        url = 'http://by.com/opt-out?email=foo%40bar.com'
        url += "&auth=" + quote_plus(get_password('foo@bar.com'))
        self.assertEqual(2, salt.call_count)
        self.assertEqual(url, opt_out)


class PasswordTests(SimpleTestCase):
    @patch('django.contrib.auth.hashers.BasePasswordHasher.salt')
    def test_valid(self, salt):
        salt.return_value = 'salty'
        email = "foo@bar.com"
        encoded = get_password(email)
        self.assertTrue(validate_password(email, encoded))


class TestDjangooptout(TestCase):
    def test_something(self):
        self.assertIsNotNone(models)

    def test_user_factory(self):
        user = factories.UserFactory()
        self.assertIsNotNone(user)
