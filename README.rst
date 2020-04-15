django-getpaid-paynow
=====================

Django-getpaid plugin for mBank payNow service

Installation
------------

.. code-block:: shell

    pip install django-getpaid-paynow

This should pull django-getpaid in case it's not installed yet.


Configuration
-------------

Add this to your settings.py:

.. code-block:: python

    GETPAID_BACKEND_SETTINGS = {
        "paynow": {
            # take these two from your merchant panel:
            "api_key": "4f36b5cd-9b0e-42fa-872d-37f8db0a3503",
            "signature_key": "f80947e4-b9a6-4bd4-a51d-6f9df8b13b16",
        },
        ...
    }

If DEBUG setting is set to True, the plugin will use the sandbox API.

