==========================
Django Opt-out application
==========================


.. image:: https://img.shields.io/pypi/v/django-opt-out.svg
        :target: https://pypi.python.org/pypi/django-opt-out

.. image:: https://img.shields.io/travis/wooyek/django-opt-out.svg
        :target: https://travis-ci.org/wooyek/django-opt-out

.. image:: https://readthedocs.org/projects/django-opt-out/badge/?version=latest
        :target: https://django-opt-out.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://coveralls.io/repos/github/wooyek/django-opt-out/badge.svg?branch=develop
        :target: https://coveralls.io/github/wooyek/django-opt-out?branch=develop
        :alt: Coveralls.io coverage

.. image:: https://codecov.io/gh/wooyek/django-opt-out/branch/develop/graph/badge.svg
        :target: https://codecov.io/gh/wooyek/django-opt-out
        :alt: CodeCov coverage

.. image:: https://api.codeclimate.com/v1/badges/0e7992f6259bc7fd1a1a/maintainability
        :target: https://codeclimate.com/github/wooyek/django-opt-out/maintainability
        :alt: Maintainability

.. image:: https://img.shields.io/github/license/wooyek/django-opt-out.svg
        :target: https://github.com/wooyek/django-opt-out/blob/develop/LICENSE
        :alt: License

.. image:: https://img.shields.io/twitter/url/https/github.com/wooyek/django-opt-out.svg?style=social
        :target: https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2Fwooyek%2Fdjango-opt-out
        :alt: Tweet about this project

.. image:: https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg
        :target: https://saythanks.io/to/wooyek

Allow everybody to unsubscribe your messages, user accounts are not required.

* Free software: MIT license
* Documentation: https://django-opt-out.readthedocs.io.


Features
--------

* A single page form for opt-out feedback submission
* Feedback options text controlled from django admin
* Predefined feedback defaults available from django manage command
* Feedback translations done in django admin
* Feedback options selection based on tags supplied to the opt-out url
* Ability to preselect a feedback option
* Ability to change selected feedback options after submission
* Ability to set tag:value pair on opt-out url and store them on submission with user feedback
* Signal to modify opt-out form before rendering
* Signal on opt-out feedback submission
* Easily overridable thank you / goodbye view
* Opt-out form with a easily overridable base template

Demo
----

To run an example project for this django reusable app, click the button below and start a demo serwer on Heroku

.. image:: https://www.herokucdn.com/deploy/button.png
    :target: https://heroku.com/deploy
    :alt: Deploy Django Opt-out example project to Heroku

.. image:: /_static/Django-Opt-out-form.png
    :target: https://heroku.com/deploy
    :alt: Deploy Django Opt-out example project to Heroku


Quickstart
----------

Install Django Opt-out application::

    pip install django-opt-out

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_opt_out.apps.DjangoOptOutConfig',
        ...
    )

Add Django Opt-out application's URL patterns:

.. code-block:: python

    from django_opt_out import urls as django_opt_out_urls


    urlpatterns = [
        ...
        url(r'^', include(django_opt_out_urls)),
        ...
    ]


Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

This package was created with Cookiecutter_ and the `wooyek/cookiecutter-django-app`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`wooyek/cookiecutter-django-app`: https://github.com/wooyek/cookiecutter-django-app
