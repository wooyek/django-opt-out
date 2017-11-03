=====
Usage
=====

To use Django Opt-out application in a project, add it to your `INSTALLED_APPS`:

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
