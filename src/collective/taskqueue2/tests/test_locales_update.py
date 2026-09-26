# -*- coding: utf-8 -*-
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from collective.taskqueue2.locales import update


class LocaleUpdateTest(unittest.TestCase):
    def setUp(self):
        self.locale_path = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.locale_path)
        patcher = mock.patch.object(update, "LOCALE_PATH", self.locale_path)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_locale_folder_setup_creates_missing_folders(self):
        (self.locale_path / "en" / "LC_MESSAGES").mkdir(parents=True)
        (self.locale_path / "de").mkdir()
        (self.locale_path / "README.rst").write_text("not a language folder")

        with mock.patch.object(update, "subprocess") as mocked_subprocess:
            update.locale_folder_setup()

        self.assertTrue((self.locale_path / "de" / "LC_MESSAGES").is_dir())
        mocked_subprocess.run.assert_called_once()
        command = mocked_subprocess.run.call_args[0][0]
        self.assertEqual(command[0], "msginit")
        self.assertIn("--locale=de", command)

    def test_locale_folder_setup_without_languages(self):
        with mock.patch.object(update, "subprocess") as mocked_subprocess:
            update.locale_folder_setup()
        mocked_subprocess.run.assert_not_called()

    def test_rebuild_pot(self):
        with mock.patch.object(update, "subprocess") as mocked_subprocess:
            update.rebuild_pot()
        command = mocked_subprocess.run.call_args[0][0]
        self.assertEqual(command[:3], ["i18ndude", "rebuild-pot", "--pot"])
        self.assertEqual(command[-2:], [update.DOMAIN, str(update.PACKAGE_PATH)])

    def test_i18ndude_can_be_configured(self):
        with mock.patch.dict(os.environ, {"I18NDUDE": "/opt/bin/i18ndude"}):
            with mock.patch.object(update, "subprocess") as mocked_subprocess:
                update.rebuild_pot()
        self.assertEqual(mocked_subprocess.run.call_args[0][0][0], "/opt/bin/i18ndude")

    def test_sync_po(self):
        catalog = self.locale_path / "en" / "LC_MESSAGES" / f"{update.DOMAIN}.po"
        catalog.parent.mkdir(parents=True)
        catalog.write_text("")

        with mock.patch.object(update, "subprocess") as mocked_subprocess:
            update.sync_po()

        command = mocked_subprocess.run.call_args[0][0]
        self.assertEqual(command[:3], ["i18ndude", "sync", "--pot"])
        self.assertIn(str(catalog), command)

    def test_sync_po_without_catalogs(self):
        with mock.patch.object(update, "subprocess") as mocked_subprocess:
            update.sync_po()
        mocked_subprocess.run.assert_not_called()

    def test_update_locale(self):
        (self.locale_path / "en" / "LC_MESSAGES").mkdir(parents=True)
        catalog = self.locale_path / "en" / "LC_MESSAGES" / f"{update.DOMAIN}.po"
        catalog.write_text("")

        with mock.patch.object(update, "subprocess") as mocked_subprocess:
            update.update_locale()

        commands = [call[0][0][1] for call in mocked_subprocess.run.call_args_list]
        self.assertEqual(commands, ["sync", "rebuild-pot"])
