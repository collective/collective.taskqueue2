# Starts the Huey consumer as a thread inside the Zope process.

import os
import pprint
import threading

from huey.bin.huey_consumer import load_huey
from huey.consumer import Consumer
from huey.consumer_options import ConsumerConfig

from collective.taskqueue2.huey_logger import LOG

# This import must remain in place in order to register the Huey tasks during
# startup !!!  Don't remove, required for task registration!
import collective.taskqueue2.huey_tasks  # noqa: F401


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
    #    "logfile": "huey.log",
    "verbose": False,
}


def get_consumer_options(environ=None, defaults=None):
    """Return the consumer options, overridden from the ``$HUEY_*`` environment.

    e.g. HUEY_WORKERS=2
         HUEY_WORKER_TYPE=process
         HUEY_PERIODIC=0
         HUEY_SCHEDULER_INTERVAL=5
         HUEY_INITIAL_DELAY=0.5
         HUEY_MAX_DELAY=10
         HUEY_BACKOFF=1.15
         HUEY_HEALTH_CHECK_INTERVAL=4
         HUEY_CHECK_WORKER_HEALTH=1
         HUEY_EXTRA_LOCKS=1
         HUEY_FLUSH_LOCKS=1
    """
    options = dict(consumer_options if defaults is None else defaults)
    for key, value in (os.environ if environ is None else environ).items():
        if not key.startswith("HUEY_"):
            continue
        option_name = key.split("HUEY_", 1)[1].lower()
        if option_name not in options:
            continue
        option_type = type(options[option_name])
        if option_type is bool:
            options[option_name] = value.lower() == "true"
        else:
            options[option_name] = option_type(value)
    return options


# The consumer runs in a thread, where signal.signal() raises a ValueError.
# Installing Huey's signal handlers must not break the Zope startup sequence.
_huey_set_signal_handlers = Consumer._set_signal_handlers


def _set_signal_handlers(self):
    """Install Huey's signal handlers, ignoring non-main-thread errors."""
    try:
        _huey_set_signal_handlers(self)
    except ValueError:
        LOG.debug("Huey signal handlers not installed (not the main thread).")


# monkey-patch huey signal handler for integration with Zope
Consumer._set_signal_handlers = _set_signal_handlers


def startup(event):
    """Start the consumer thread, logging the reason if it fails."""
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
    )
    if is_huey_consumer:
        options = get_consumer_options()
        huey_taskqueue = load_huey("collective.taskqueue2.huey_config.huey_taskqueue")

        config = ConsumerConfig(**options)
        config.validate()
        config.setup_logger()
        consumer = huey_taskqueue.create_consumer(**config.values)

        th = threading.Thread(
            target=consumer.run, name="huey-consumer", daemon=True
        )
        th.start()

        LOG.info(f"Consumer options: {pprint.pformat(options)}")
        LOG.info("collective.taskqueue2: consumer thread started.")
    else:
        LOG.debug(
            "collective.taskqueue2 installed but this instance is not configured as a consumer. Set HUEY_CONSUMER=1 in your environment."
        )
