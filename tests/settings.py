# -*- coding: utf-8
# Based on https://github.com/wooyek/cookiecutter-django-website by Janusz Skonieczny

import logging
import os
from pathlib import Path

import environ

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s', datefmt='%H:%M:%S')
logging.getLogger().setLevel(logging.DEBUG)
logging.disable(logging.NOTSET)

logging.debug("Settings loading: %s" % __file__)

print("""
╭─────────{border}─╮
│ Loading {name} │
╰─────────{border}─╯
""".format(name=__name__, border='─' * len(__name__)))

# This will read missing environment variables from a file
# We want to do this before loading any base settings as they may depend on environment
# NOTE: Django test runner override DEBUG to False, use override_settings decorator to change this
environ.Env.read_env(str(Path(__file__).with_suffix('.env')), DEBUG='False')

# We rely here on example_project base settings
from website.settings.base import *  # noqa: F402, F403 isort:skip

if "DATABASE_URL" not in os.environ:  # pragma: no cover
    DATABASES['default']['NAME'] = ':memory:'  # noqa F405

ROOT_URLCONF = 'tests.urls'

# https://docs.djangoproject.com/en/1.6/topics/email/#console-backend
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
LOGGING['handlers']['mail_admins']['email_backend'] = 'django.core.mail.backends.dummy.EmailBackend'  # noqa: F405

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
