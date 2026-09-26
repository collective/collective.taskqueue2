# Logger for huey taskqueue

import logging
import os


LOG = logging.getLogger("huey")

VALID_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def configure_huey_logger(log_level=None, logger=LOG):
    """Set the log level of ``logger``.

    ``log_level`` defaults to the value of the ``$HUEY_LOG_LEVEL`` environment
    variable. A missing or empty level leaves the logger untouched.
    """
    if log_level is None:
        log_level = os.environ.get("HUEY_LOG_LEVEL")
    if not log_level:
        return logger
    if log_level not in VALID_LOG_LEVELS:
        raise ValueError(f"Invalid log level for $HUEY_LOG_LEVEL ({log_level})")
    logger.setLevel(getattr(logging, log_level))
    return logger


configure_huey_logger()
