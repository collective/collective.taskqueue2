# bin/instance run scripts/huey_consumer.py

import logging
import os
import signal
import threading

from huey.consumer import Consumer
from huey.bin.huey_consumer import load_huey
from huey.consumer_options import ConsumerConfig

# don't remove, required for task registration
from unibo.magazine.huey_tasks import schedule_browser_view
from unibo.magazine.huey_logger import LOG




# monkey-patch huey
def my_set_signal_handlers(self):
    """Ignore signal errors from Huey"""
    try:
        signal.signal(signal.SIGTERM, self._handle_stop_signal)
        signal.signal(signal.SIGINT, signal.default_int_handler)
        if hasattr(signal, "SIGHUP"):
            signal.signal(signal.SIGHUP, self._handle_restart_signal)
    except ValueError:
        print("Huey signal exception ignored")


Consumer._set_signal_handlers = my_set_signal_handlers


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
    "workers": 4,
    "logfile": "huey.log",
    "verbose": False,
}

# load huey configuration from huey_tasks.py (code above)

is_huey_consumer = os.environ.get("HUEY_CONSUMER", "0") in ("1", "True", "true", "on")
if is_huey_consumer:
    huey_taskqueue = load_huey("unibo.magazine.huey_config.huey_taskqueue")

    config = ConsumerConfig(**consumer_options)
    config.validate()
    config.setup_logger()
    consumer = huey_taskqueue.create_consumer(**config.values)

    th = threading.Thread(target=consumer.run)
    th.start()

    LOG.info("Started Huey consumer thread")
else:
    LOG.info("NO HUEY CONSUMER")