#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-opt-out
------------

Tests for `django-opt-out` models module.
"""

from django.test import TestCase

from django_opt_out import models
from tests import factories


class TestDjangooptout(TestCase):

    def test_something(self):
        self.assertIsNotNone(models)

    def test_user_factory(self):
        user = factories.UserFactory()
        self.assertIsNotNone(user)
