# -*- coding: utf-8 -*-
"""Rebuild and synchronize the translation catalogs using ``i18ndude``."""

import os
from pathlib import Path
import subprocess


DOMAIN = "collective.taskqueue2"
PACKAGE_PATH = Path(__file__).resolve().parent.parent
LOCALE_PATH = PACKAGE_PATH / "locales"

# ignore node_modules files resulting in errors
EXCLUDES = "*.html *json-schema*.xml"


def i18ndude():
    """Return the i18ndude executable to use."""
    return os.environ.get("I18NDUDE", "i18ndude")


def locale_folder_setup():
    """Create the missing ``LC_MESSAGES`` folders for new languages."""
    for lang in sorted(p for p in LOCALE_PATH.iterdir() if p.is_dir()):
        lc_messages_path = lang / "LC_MESSAGES"
        if lc_messages_path.is_dir():
            continue
        lc_messages_path.mkdir()
        subprocess.run(
            [
                "msginit",
                f"--locale={lang.name}",
                f"--input={LOCALE_PATH}/{DOMAIN}.pot",
                f"--output={lc_messages_path}/{DOMAIN}.po",
            ],
            check=False,
        )


def rebuild_pot():
    """Rebuild the ``.pot`` template from the sources."""
    subprocess.run(
        [
            i18ndude(),
            "rebuild-pot",
            "--pot",
            f"{LOCALE_PATH}/{DOMAIN}.pot",
            "--exclude",
            EXCLUDES,
            "--create",
            DOMAIN,
            str(PACKAGE_PATH),
        ],
        check=False,
    )


def sync_po():
    """Sync the translations catalogs with the ``.pot`` template."""
    catalogs = sorted(str(p) for p in LOCALE_PATH.glob(f"*/LC_MESSAGES/{DOMAIN}.po"))
    if not catalogs:
        return
    subprocess.run(
        [
            i18ndude(),
            "sync",
            "--pot",
            f"{LOCALE_PATH}/{DOMAIN}.pot",
            *catalogs,
        ],
        check=False,
    )


def update_locale():
    """Entry point of the ``update_locale`` console script."""
    locale_folder_setup()
    sync_po()
    rebuild_pot()
