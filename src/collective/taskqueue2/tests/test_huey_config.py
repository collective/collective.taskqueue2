# -*- coding: utf-8 -*-
import os
import unittest
from unittest import mock

from huey import FileHuey, MemoryHuey, RedisHuey, SqliteHuey

from collective.taskqueue2.huey_config import get_huey_taskqueue


def environ_without_huey(**extra):
    environ = {
        key: value for key, value in os.environ.items() if not key.startswith("HUEY_")
    }
    environ.update(extra)
    return environ


class GetHueyTaskqueueTest(unittest.TestCase):
    def test_sqlite_scheme(self):
        queue = get_huey_taskqueue("sqlite:///tmp/huey-test.sqlite")
        self.assertIsInstance(queue, SqliteHuey)
        self.assertEqual(queue.storage_kwargs["filename"], "/tmp/huey-test.sqlite")

    def test_redis_scheme(self):
        queue = get_huey_taskqueue("redis://:secret@localhost:6379/3")
        self.assertIsInstance(queue, RedisHuey)
        self.assertEqual(queue.storage_kwargs["host"], "localhost")
        self.assertEqual(queue.storage_kwargs["port"], 6379)
        self.assertEqual(queue.storage_kwargs["password"], "secret")
        self.assertEqual(queue.storage_kwargs["db"], 3)

    def test_memory_scheme(self):
        self.assertIsInstance(get_huey_taskqueue("memory://"), MemoryHuey)

    def test_file_scheme(self):
        queue = get_huey_taskqueue("file:///tmp/huey-queue")
        self.assertIsInstance(queue, FileHuey)
        self.assertEqual(queue.storage_kwargs["path"], "/tmp/huey-queue")

    def test_unknown_scheme(self):
        with self.assertRaises(ValueError) as cm:
            get_huey_taskqueue("amqp://localhost")
        self.assertIn("HUEY_TASKQUEUE_URL", str(cm.exception))

    def test_url_from_environment(self):
        environ = environ_without_huey(HUEY_TASKQUEUE_URL="memory://")
        with mock.patch.dict(os.environ, environ, clear=True):
            self.assertIsInstance(get_huey_taskqueue(), MemoryHuey)

    def test_default_url(self):
        with mock.patch.dict(os.environ, environ_without_huey(), clear=True):
            queue = get_huey_taskqueue()
        self.assertIsInstance(queue, SqliteHuey)
        self.assertEqual(queue.storage_kwargs["filename"], "/tmp/huey_queue.sqlite")
