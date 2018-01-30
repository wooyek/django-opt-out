#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

import django
import pytest
from django.test import SimpleTestCase, TestCase
from django.test.utils import override_settings
from django_powerbank.testing.base import MigrationsCheckMx
from mock import patch
from six.moves.urllib.parse import quote_plus

from django_opt_out import factories
from django_opt_out.utils import get_opt_out_path, get_password, validate_password, get_opt_out_url


@pytest.mark.django_db
class MigrationsCheckTests(MigrationsCheckMx, TestCase):

    @unittest.skipIf(django.VERSION[0] < 2, "There maybe difference in migrations state for older versions of django")
    def test_missing_migrations(self):
        super().test_missing_migrations()


@override_settings(OUT_OUT_REQUIRE_CONFIRMATION=False)
class TestOptOutUrl(SimpleTestCase):
    def test_no_tags(self):
        url = get_opt_out_path('foo@bar.com')
        self.assertEqual(url, '/opt-out/?email=foo%40bar.com')

    def test_one_tag(self):
        url = get_opt_out_path('foo2@bar.com', 'notification')
        self.assertEqual(url, '/opt-out/?email=foo2%40bar.com&tag=notification')

    def test_multiple_tags(self):
        url = get_opt_out_path('foo@bar.com', 'notifications', 'comments')
        self.assertEqual(url, '/opt-out/?email=foo%40bar.com&tag=notifications&tag=comments')

    def test_many_tags(self):
        url = get_opt_out_path('foo@bar.com', 'notifications', 'comments')
        self.assertEqual(url, '/opt-out/?email=foo%40bar.com&tag=notifications&tag=comments')

    def test_tags_values(self):
        url = get_opt_out_path('foo@bar.com', 'notifications:123', 'comments:owner')
        self.assertEqual(url, '/opt-out/?email=foo%40bar.com&tag=notifications%3A123&tag=comments%3Aowner')

    @override_settings(OPT_OUT_BASE_URL='https://ex.com')
    def test_settings_base_url(self):
        url = get_opt_out_url('foo@bar.com')
        self.assertEqual(url, 'https://ex.com/opt-out/?email=foo%40bar.com')

    @override_settings(OUT_OUT_REQUIRE_CONFIRMATION=True)
    @patch('django.contrib.auth.hashers.BasePasswordHasher.salt')
    def test_password_in_url(self, salt):
        salt.return_value = 'salty'
        opt_out = get_opt_out_url('foo@bar.com', base_url='http://by.com')
        url = 'http://by.com/opt-out/?email=foo%40bar.com'
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


class OptOutFeedbackTest(TestCase):
    def test_trans_fallback(self):
        item = factories.OptOutFeedbackFactory()
        self.assertEqual(item.text, item.trans())

    def test_trans(self):
        text = 'Zażółć gęślą jaźń'
        item = factories.OptOutFeedbackTranslationFactory(text=text).feedback
        trans = item.trans('pl')
        self.assertEqual(text, trans)
        self.assertNotEqual(item.text, trans)
