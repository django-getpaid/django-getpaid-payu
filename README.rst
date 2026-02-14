.. warning::

    **This package has been discontinued.**

===================
django-getpaid-payu
===================

This package is no longer maintained. It has been superseded by the new
``python-getpaid`` ecosystem, which provides a framework-agnostic core and
separate gateway plugins.

Migration
=========

To migrate, replace ``django-getpaid-payu`` with the following packages:

1. `python-getpaid-core <https://pypi.org/project/python-getpaid-core/>`_ —
   framework-agnostic payment processing library
2. `django-getpaid <https://pypi.org/project/django-getpaid/>`_ — Django
   framework adapter
3. `python-getpaid-payu <https://pypi.org/project/python-getpaid-payu/>`_ —
   PayU gateway plugin

.. code-block:: shell

    pip install python-getpaid-core django-getpaid python-getpaid-payu

For more information, visit the
`python-getpaid GitHub organization <https://github.com/django-getpaid>`_.

License
=======

MIT
