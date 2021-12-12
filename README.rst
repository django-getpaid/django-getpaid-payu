.. image:: https://img.shields.io/pypi/v/django-getpaid-payu.svg
    :target: https://pypi.org/project/django-getpaid-payu/
    :alt: Latest PyPI version
.. image:: https://github.com/django-getpaid/django-getpaid-payu/actions/workflows/run_tox.yml/badge.svg
    :target: https://github.com/django-getpaid/django-getpaid-payu/actions/
.. image:: https://img.shields.io/pypi/wheel/django-getpaid-payu.svg
    :target: https://pypi.org/project/django-getpaid-payu/
.. image:: https://img.shields.io/pypi/l/django-getpaid-payu.svg
    :target: https://pypi.org/project/django-getpaid-payu/

===================
django-getpaid-payu
===================

Django-getpaid plugin for PayU service.

.. note::

    This is Alpha-quality software. You are more than welcome to `send PRs <https://github.com/django-getpaid/django-getpaid-payu>`_
    with fixes and new features.

Installation
============

First make sure that `django-getpaid <https://django-getpaid.readthedocs.io/>`_ is installed and configured.

Then, simply install the plugin:

.. code-block:: shell

    pip install django-getpaid-payu

This should pull django-getpaid in case it's not installed yet.


Configuration
=============

Add ``"getpaid_payu"`` to your ``INSTALLED_APPS`` and add plugin configuration.

.. code-block:: python

    # settings.py

    INSTALLED_APPS = [
        # ...
        "getpaid",
        "getpaid_payu",
    ]

    GETPAID_BACKEND_SETTINGS = {
        "getpaid_payu": {
            # take these from your merchant panel:
            "pos_id": 12345,
            "second_key": "91ae651578c5b5aa93f2d38a9be8ce11",
            "oauth_id": 12345,
            "oauth_secret": "12f071174cb7eb79d4aac5bc2f07563f",
        },
        # ...
    }

.. note::

    If ``DEBUG`` setting is set to ``True``, the plugin will use the sandbox API.

That should be enough to make your ``django-getpaid`` integration use new plugin
and allow you to choose PayU for supported currencies.

Other settings
--------------

You can change additional settings for the plugin:

confirmation_method
~~~~~~~~~~~~~~~~~~~

* PUSH - paywall will send status updates to the callback endpoint hence updating status automatically
* PULL - each Payment has to be verified by calling its ``fetch_and_update_status()``, eg. from a Celery task.

Default: PUSH

paywall_method
~~~~~~~~~~~~~~

* REST - payment will be created using REST api call to paywall
* POST - an extra screen will be displayed with a confirmation button that will
  send all Payment params to paywall using POST. This is not recommended by PayU.

Licence
=======

MIT

Authors
=======

`Dominik Kozaczko <https://github.com/dekoza/>`_
