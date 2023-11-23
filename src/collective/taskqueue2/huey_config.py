import furl
import os

from collective.taskqueue2.huey_logger import LOG


default_huey_url = "sqlite:///tmp/huey_queue.sqlite"

huey_url = os.environ.get("HUEY_TASKQUEUE_URL", default_huey_url)
parsed_url = furl.furl(huey_url)
scheme = parsed_url.scheme

if scheme == "sqlite":
    from huey import SqliteHuey

    huey_taskqueue = SqliteHuey(filename=str(parsed_url.path))

elif scheme == "redis":
    # requires redis-p
    from huey import RedisHuey
    try:
        pass
    except Exception:
        msg = "For using Redis, you need to install py-redis"
        raise RuntimeError(msg)

    huey_taskqueue = RedisHuey(
        host=parsed_url.host,
        port=parsed_url.port,
        password=parsed_url.password,
        db=int(str(parsed_url.path).lstrip("/")),
    )

elif scheme == "memory":
    # requires redis-py
    from huey import MemoryHuey

    huey_taskqueue = MemoryHuey()

elif scheme == "file":
    from huey import FileHuey

    huey_taskqueue = FileHuey(path=str(parsed_url.path))

else:
    raise ValueError(
        f"No proper configuration for $HUEY_TASKQUEUE_URL found ({huey_url}"
    )

LOG.info(f"Using taskqueue {huey_taskqueue}, {huey_taskqueue.__dict__}")
