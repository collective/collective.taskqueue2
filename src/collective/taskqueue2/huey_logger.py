import os
import logging

huey_log_level = os.environ.get("HUEY_LOG_LEVEL")

LOG = logging.getLogger("huey")
if huey_log_level:
    if not  huey_log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        raise ValueError(f"Invalid log level for $HUEY_LOG_LEVEL ({huey_log_level})")
    LOG.setLevel(getattr(logging, huey_log_level))

