Development
===========

collective.taskqueue2 is developed against Plone 6.2 without buildout. The
complete development environment is managed by `uv <https://docs.astral.sh/uv/>`_
and driven by the ``Makefile``.


Quick start
-----------

::

    $ make dev

This downloads the Plone 6.2 constraints file, creates ``.venv``, installs
Plone and this package, creates the Zope WSGI instance in ``instance`` and
starts it:

    Plone 6.2.2 is running on http://127.0.0.1:8080/
    login: admin / admin

Stop it with ``make stop``, run it in the foreground (Ctrl-C to stop) with
``make fg``. ``make help`` lists all targets.


Makefile targets
----------------

=================  ======================================================
Target             Description
=================  ======================================================
``make dev``       install everything and run the instance in the background
``make start``     start the instance (idempotent, waits until it answers)
``make stop``      stop the instance
``make restart``   stop and start the instance
``make status``    report whether the instance is running
``make fg``        run the instance in the foreground
``make test``      run the test suite and show the coverage report
``make coverage``  the same, but fails below the ``COVERAGE_MIN`` gate (CI)
``make lint``      run ruff
``make format``    apply the ruff fixes
``make build``     build sdist and wheel into ``dist/``
``make clean``     remove the instance, the coverage files and caches
=================  ======================================================


Variables
---------

All paths, versions and the runtime configuration of the instance can be
overridden on the command line::

    $ make dev PLONE_RELEASE=6.2.2 PYTHON_VERSION=3.13 PORT=9090
    $ make dev HUEY_TASKQUEUE_URL=redis://localhost:6379/0
    $ make coverage COVERAGE_MIN=99

===================  ======================================================
Variable             Default
===================  ======================================================
``PLONE_VERSION``    ``6.2`` (used for the constraints URL)
``PLONE_RELEASE``    ``6.2.2`` (the installed Plone version)
``PYTHON_VERSION``   ``3.13``
``PORT``             ``8080``
``HUEY_CONSUMER``    ``1`` for the dev instance
``HUEY_TASKQUEUE_URL`` ``memory://`` for the dev instance
``HUEY_LOG_LEVEL``   ``INFO``
``COVERAGE_MIN``     ``99``
===================  ======================================================


What ``make install`` does
--------------------------

``uv`` cannot read a remote constraints file, so the Plone constraints are
downloaded to ``constraints-plone-6.2.txt`` first (that file is generated and
therefore not under version control)::

    curl --fail --location --show-error \
        -o constraints-plone-6.2.txt \
        https://dist.plone.org/release/6.2-latest/constraints.txt
    uv venv --python 3.13 .venv
    uv pip install --python .venv/bin/python -c constraints-plone-6.2.txt "Plone==6.2.2"
    uv pip install --python .venv/bin/python -c constraints-plone-6.2.txt -e ".[test]"

The package itself is installed in editable mode, so source changes are picked
up without reinstalling.


Running tests without the Makefile
----------------------------------

::

    $ .venv/bin/zope-testrunner --test-path=src -s collective.taskqueue2 -v1
    $ .venv/bin/coverage run .venv/bin/zope-testrunner \
        --test-path=src -s collective.taskqueue2
    $ .venv/bin/coverage report -m

The tests use ``HUEY_TASKQUEUE_URL=memory://`` (set in
``collective.taskqueue2.tests``), so no Redis and no queue database in ``/tmp``
is required. Test layers live in ``collective.taskqueue2.testing``.


Console scripts
---------------

``update_locale`` rebuilds the translation catalogs, it requires
``i18ndude`` (and ``msginit``) in the path::

    $ .venv/bin/update_locale
    $ I18NDUDE=/path/to/i18ndude .venv/bin/update_locale


Instances as a queue consumer
-----------------------------

``HUEY_CONSUMER=1`` makes the instance run the Huey consumer as an additional
thread. ``make dev`` sets this, so queued tasks are executed right away. In
production set it only on the ZEO client(s) that should consume the queue.
