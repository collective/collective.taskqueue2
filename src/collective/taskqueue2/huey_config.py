from collective.taskqueue2.huey_logger import LOG
from huey import FileHuey
from huey import MemoryHuey
from huey import RedisHuey
from huey import SqliteHuey

import furl
import os


default_huey_url = "sqlite:///tmp/huey_queue.sqlite"


def get_huey_taskqueue():
    """Return a Huey taskqueue instance"""

    huey_url = os.environ.get("HUEY_TASKQUEUE_URL", default_huey_url)
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
            f"No proper configuration for $HUEY_TASKQUEUE_URL found ({huey_url}"
        )


huey_taskqueue = get_huey_taskqueue()

LOG.info(f"Using taskqueue {huey_taskqueue}, {huey_taskqueue.__dict__}")
