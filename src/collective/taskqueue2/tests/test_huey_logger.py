# -*- coding: utf-8 -*-
import logging
import os
import unittest
from unittest import mock

from collective.taskqueue2.huey_logger import LOG, configure_huey_logger


class ConfigureHueyLoggerTest(unittest.TestCase):
    def setUp(self):
        self.level = LOG.level

    def tearDown(self):
        LOG.setLevel(self.level)

    def test_explicit_valid_level(self):
        self.assertIs(configure_huey_logger("DEBUG"), LOG)
        self.assertEqual(LOG.level, logging.DEBUG)

    def test_explicit_invalid_level(self):
        with self.assertRaises(ValueError) as cm:
            configure_huey_logger("NOT_A_LOG_LEVEL")
        self.assertIn("HUEY_LOG_LEVEL", str(cm.exception))

    def test_explicit_empty_level_keeps_level(self):
        LOG.setLevel(logging.WARNING)
        self.assertIs(configure_huey_logger(""), LOG)
        self.assertEqual(LOG.level, logging.WARNING)

    def test_level_from_environment(self):
        with mock.patch.dict(os.environ, {"HUEY_LOG_LEVEL": "ERROR"}):
            self.assertIs(configure_huey_logger(), LOG)
        self.assertEqual(LOG.level, logging.ERROR)

    def test_no_level_configured(self):
        environ = {
            key: value
            for key, value in os.environ.items()
            if key != "HUEY_LOG_LEVEL"
        }
        LOG.setLevel(logging.WARNING)
        with mock.patch.dict(os.environ, environ, clear=True):
            self.assertIs(configure_huey_logger(), LOG)
        self.assertEqual(LOG.level, logging.WARNING)
