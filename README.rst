################
pyramid_mongokit
################

.. image:: https://travis-ci.org/hadrien/pyramid_mongokit.png?branch=master
   :target: https://travis-ci.org/hadrien/pyramid_mongokit

.. image:: https://coveralls.io/repos/hadrien/pyramid_mongokit/badge.png
  :target: https://coveralls.io/r/hadrien/pyramid_mongokit

.. image:: https://pypip.in/d/pyramid_mongokit/badge.png
   :target: https://crate.io/packages/pyramid_mongokit/


A simple Pyramid extension that registers a mongokit connection as an
attribute of the request object.

Expects ``MONGO_URI`` in ``os.environ``.

If provided as environment variables, ``MONGO_DB_PREFIX`` will be used as
prefix for any databases and ``MONGO_DB_NAME`` for database name.

Source code & example on https://github.com/hadrien/pyramid_mongokit