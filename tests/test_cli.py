#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `django-opt-out` package."""

import pytest
from click.testing import CliRunner
from django.test import TestCase

import django_opt_out
from django_opt_out import cli, factories, models

django_opt_out.__version__


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/wooyek/cookiecutter-pylib')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'django_opt_out.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output


class SetupDefaultsTests(TestCase):
    def test_tags(self):
        from django_opt_out.management.commands.opt_out_feedback_defaults import Command
        Command().import_all()
        self.assertEqual(3, models.OptOutTag.objects.count())
        self.assertEqual(8, models.OptOutFeedback.objects.count())
        self.assertEqual(8, models.OptOutFeedbackTranslation.objects.count())

    def test_ignore_call_on_data(self):
        factories.OptOutTagFactory()
        from django_opt_out.management.commands.opt_out_feedback_defaults import Command
        Command().handle(force=False, on_empty=True)

    def test_failt_on_existing_data(self):
        factories.OptOutTagFactory()
        from django_opt_out.management.commands.opt_out_feedback_defaults import Command
        self.assertRaises(AssertionError, Command().handle, force=False, on_empty=False)
