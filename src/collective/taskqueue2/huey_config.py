from collective.taskqueue2.huey_logger import LOG
from huey import FileHuey
from huey import MemoryHuey
from huey import RedisHuey
from huey import SqliteHuey

import furl
import os


default_huey_url = "sqlite:///tmp/huey_queue.sqlite"

huey_url = os.environ.get("HUEY_TASKQUEUE_URL", default_huey_url)
parsed_url = furl.furl(huey_url)
scheme = parsed_url.scheme

if scheme == "sqlite":
    huey_taskqueue = SqliteHuey(filename=str(parsed_url.path))
elif scheme == "redis":
    # requires redis-py
    huey_taskqueue = RedisHuey(
        host=parsed_url.host,
        port=parsed_url.port,
        password=parsed_url.password,
        db=int(str(parsed_url.path).lstrip("/")),
    )
elif scheme == "memory":
    huey_taskqueue = MemoryHuey()
elif scheme == "file":
    huey_taskqueue = FileHuey(path=str(parsed_url.path))
else:
    raise ValueError(
        f"No proper configuration for $HUEY_TASKQUEUE_URL found ({huey_url}"
    )

LOG.info(f"Using taskqueue {huey_taskqueue}, {huey_taskqueue.__dict__}")
