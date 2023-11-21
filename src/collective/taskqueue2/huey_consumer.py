# bin/instance run scripts/huey_consumer.py

from collective.taskqueue2.huey_logger import LOG
from huey.bin.huey_consumer import load_huey
from huey.consumer import Consumer
from huey.consumer_options import ConsumerConfig

# don't remove, required for task registration
import os
import signal
import threading


# This import must remain in place in order to register the Huey tasks during
# startup !!!
import collective.taskqueue2.huey_tasks # noqa: F401


# monkey-patch huey signal handler for integration with Zope
def my_set_signal_handlers(self):
    """Ignore signal errors from Huey"""
    try:
        signal.signal(signal.SIGTERM, self._handle_stop_signal)
        signal.signal(signal.SIGINT, signal.default_int_handler)
        if hasattr(signal, "SIGHUP"):
            signal.signal(signal.SIGHUP, self._handle_restart_signal)
    except ValueError:
        LOG.debug("Huey signal exception ignored")


Consumer._set_signal_handlers = my_set_signal_handlers


# huey consumer configuration options
consumer_options = {
    "backoff": 1.15,
    "check_worker_health": True,
    "extra_locks": None,
    "flush_locks": False,
    "health_check_interval": 4,
    "initial_delay": 0.1,
    "max_delay": 1.0,
    "periodic": True,
    "scheduler_interval": 1,
    "worker_type": "thread",
    "workers": 1,
    "logfile": "huey.log",
    "verbose": False,
}


# startup handler for starting Huey consumer thread
def startup(event):
    try:
        _startup(event)
    except Exception as e:
        LOG.error(f"collective.taskqueue2: error starting consumer thread: {e}")
        raise


def _startup(event):
    is_huey_consumer = os.environ.get("HUEY_CONSUMER", "0") in (
        "1",
        "True",
        "true",
        "on",
    )  # noqa: E501
    if is_huey_consumer:
        huey_taskqueue = load_huey("collective.taskqueue2.huey_config.huey_taskqueue")

        config = ConsumerConfig(**consumer_options)
        config.validate()
        config.setup_logger()
        consumer = huey_taskqueue.create_consumer(**config.values)

        th = threading.Thread(target=consumer.run)
        th.start()

        LOG.info("collective.taskqueue2: consumer thread started.")
    else:
        LOG.debug(
            "collective.taskqueue2 installed but this instance is not configured as a consumer. Set HUEY_CONSUMER=1 in your environment."
        )
