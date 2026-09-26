import os

import furl
from huey import FileHuey, MemoryHuey, RedisHuey, SqliteHuey

from collective.taskqueue2.huey_logger import LOG


default_huey_url = "sqlite:///tmp/huey_queue.sqlite"


def get_huey_taskqueue(url=None):
    """Return a Huey taskqueue instance for ``url``.

    ``url`` defaults to the value of the ``$HUEY_TASKQUEUE_URL`` environment
    variable falling back to :data:`default_huey_url`.
    """
    if url is None:
        url = os.environ.get("HUEY_TASKQUEUE_URL")
    huey_url = url or default_huey_url
    parsed_url = furl.furl(huey_url)
    scheme = parsed_url.scheme

    if scheme == "sqlite":
        return SqliteHuey(filename=str(parsed_url.path))
    elif scheme == "redis":
        # requires redis-py
        return RedisHuey(
            host=parsed_url.host,
            port=parsed_url.port,
            password=parsed_url.password,
            db=int(str(parsed_url.path).lstrip("/")),
        )
    elif scheme == "memory":
        return MemoryHuey()
    elif scheme == "file":
        return FileHuey(path=str(parsed_url.path))
    else:
        raise ValueError(
            f"No proper configuration for $HUEY_TASKQUEUE_URL found ({huey_url})"
        )


huey_taskqueue = get_huey_taskqueue()

LOG.info(f"Using taskqueue {huey_taskqueue}, {huey_taskqueue.__dict__}")
