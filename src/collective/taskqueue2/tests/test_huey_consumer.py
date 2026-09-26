# -*- coding: utf-8 -*-
import os
import signal
import unittest
from unittest import mock

from huey.consumer import Consumer

from collective.taskqueue2 import huey_consumer
from collective.taskqueue2.huey_consumer import get_consumer_options, startup


class GetConsumerOptionsTest(unittest.TestCase):
    def test_defaults(self):
        options = get_consumer_options({})
        self.assertEqual(options["workers"], 1)
        self.assertEqual(options["worker_type"], "thread")
        self.assertTrue(options["periodic"])

    def test_overrides_from_environment(self):
        options = get_consumer_options(
            {
                "HUEY_WORKERS": "3",
                "HUEY_WORKER_TYPE": "process",
                "HUEY_PERIODIC": "false",
                "HUEY_VERBOSE": "true",
                "HUEY_INITIAL_DELAY": "0.5",
            }
        )
        self.assertEqual(options["workers"], 3)
        self.assertEqual(options["worker_type"], "process")
        self.assertFalse(options["periodic"])
        self.assertTrue(options["verbose"])
        self.assertEqual(options["initial_delay"], 0.5)

    def test_ignores_unrelated_variables(self):
        options = get_consumer_options(
            {"HOME": "/home/me", "HUEY_NOT_AN_OPTION": "1"}
        )
        self.assertEqual(options, get_consumer_options({}))

    def test_reads_os_environ_by_default(self):
        with mock.patch.dict(os.environ, {"HUEY_WORKERS": "7"}):
            self.assertEqual(get_consumer_options()["workers"], 7)

    def test_custom_defaults(self):
        options = get_consumer_options(
            {"HUEY_WORKERS": "2"}, defaults={"workers": 5, "verbose": False}
        )
        self.assertEqual(options["workers"], 2)
        self.assertFalse(options["verbose"])
        self.assertNotIn("periodic", options)


class FakeConsumer:
    """Minimal stand-in for ``huey.consumer.Consumer``."""

    _signals = (signal.SIGINT, signal.SIGTERM)
    worker_type = "thread"

    def _handle_stop_signal(self, signum, frame):
        pass

    def _handle_graceful_signal(self, signum, frame):
        pass

    def _handle_restart_signal(self, signum, frame):
        pass


class SignalHandlerTest(unittest.TestCase):
    def test_signal_handlers_are_installed(self):
        with mock.patch.object(signal, "signal") as mocked_signal:
            Consumer._set_signal_handlers(FakeConsumer())
        self.assertEqual(mocked_signal.call_count, 3)

    def test_value_error_from_a_non_main_thread_is_ignored(self):
        with mock.patch.object(
            signal,
            "signal",
            side_effect=ValueError("signal only works in main thread"),
        ):
            with self.assertLogs("huey", level="DEBUG") as cm:
                Consumer._set_signal_handlers(FakeConsumer())
        self.assertIn("signal handlers not installed", cm.output[0])


class StartupTest(unittest.TestCase):
    def test_instance_without_consumer_role(self):
        with mock.patch.dict(os.environ, {"HUEY_CONSUMER": "0"}):
            with self.assertLogs("huey", level="DEBUG") as cm:
                startup(None)
        self.assertIn("not configured as a consumer", cm.output[0])

    def test_huey_consumer_unset(self):
        environ = {
            key: value for key, value in os.environ.items() if key != "HUEY_CONSUMER"
        }
        with mock.patch.dict(os.environ, environ, clear=True):
            with self.assertLogs("huey", level="DEBUG") as cm:
                startup(None)
        self.assertIn("not configured as a consumer", cm.output[0])

    def test_consumer_thread_is_started(self):
        huey_instance = mock.MagicMock()
        consumer = huey_instance.create_consumer.return_value
        thread = mock.MagicMock()
        with mock.patch.dict(os.environ, {"HUEY_CONSUMER": "1"}):
            with mock.patch.object(
                huey_consumer, "load_huey", return_value=huey_instance
            ):
                with mock.patch.object(
                    huey_consumer.threading, "Thread", return_value=thread
                ) as thread_class:
                    with mock.patch.object(
                        huey_consumer.ConsumerConfig, "setup_logger"
                    ):
                        with self.assertLogs("huey", level="INFO") as cm:
                            startup(None)

        thread_class.assert_called_once_with(
            target=consumer.run, name="huey-consumer", daemon=True
        )
        thread.start.assert_called_once_with()
        huey_instance.create_consumer.assert_called_once()
        self.assertTrue(
            any("consumer thread started" in line for line in cm.output), cm.output
        )

    def test_startup_error_is_logged_and_reraised(self):
        with mock.patch.object(
            huey_consumer, "_startup", side_effect=RuntimeError("boom")
        ):
            with self.assertLogs("huey", level="ERROR") as cm:
                with self.assertRaises(RuntimeError):
                    startup(None)
        self.assertIn("error starting consumer thread", cm.output[0])
