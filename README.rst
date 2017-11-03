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

Allow everybody to unsubscribe your messages, user accounts are not required.

* Free software: MIT license
* Documentation: https://django-opt-out.readthedocs.io.


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

Features
--------

* TODO

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
