Changelog
=========


1.0a2 (unreleased)
------------------

Modernization for Plone 6.2 and Python 3.10+:

- Packaging moved from ``setup.py`` to ``pyproject.toml`` (PEP 621).
- The ``collective`` namespace package is a PEP 420 namespace package, the
  ``pkg_resources`` dependency is gone.
- The ZCML is registered via the ``plone.autoinclude.plugin`` entry point.
- Dropped Plone 5.2 support and the buildout based development setup
  (``setup.py``, ``base.cfg``, ``buildout.cfg``, ``test_plone*.cfg``,
  ``constraints_plone*.txt``, ``requirements*.txt``, ``tox.ini``,
  ``.travis.yml``).
- Development and CI now use ``uv``, driven by the ``Makefile`` (``make dev``,
  ``make test``, ``make coverage``, ``make lint``).
- ``huey`` 3.x support: the consumer options are read from the environment at
  startup instead of at import time and the patched signal handler is now a
  wrapper around the Huey implementation, so it keeps Huey's graceful signal
  handling.
- Deprecated Plone imports replaced (``plone.base.interfaces`` instead of
  ``Products.CMFPlone.interfaces``, ``plone.testing.zope`` instead of
  ``plone.testing.z2``).
- ``locales/update.py`` rewritten on ``pathlib`` without import side effects.
- Test suite replaced by real tests for all modules, coverage gate at 99 %.
- ``huey_tasks.schedule_browser_view()`` logs correctly and only aborts on
  ``Exception`` instead of on any ``BaseException``.

  [zopyx]


1.0a1 (unreleased)
------------------

- Initial release.
  [zopyx]
