# bin/instance run scripts/huey_consumer.py

from collective.taskqueue2.huey_config import huey_taskqueue
from collective.taskqueue2.huey_logger import LOG
from huey import crontab
from Testing.makerequest import makerequest
from zope.component.hooks import setSite

import plone.api
import time
import transaction
import Zope2


# Start huey consumer as thread


@huey_taskqueue.on_startup()
def on_startup():
    LOG.info("ON STARTUP")


@huey_taskqueue.pre_execute()
def pre_execute_hook(task):
    #    LOG.info(f"PRE HOOK: {task}")
    pass


@huey_taskqueue.post_execute()
def post_execute_hook(task, task_value, exc):
    #    LOG.info(f"POST HOOK {task=} {task_value=} {exc=}")
    pass


@huey_taskqueue.periodic_task(crontab(minute="*", hour="*"))
def dump_queue_stats():
    data = dict(
        pending=len(huey_taskqueue.pending()),
        scheduled=len(huey_taskqueue.scheduled()),
    )
    LOG.info(f"Taskqueue stats: {data}")


@huey_taskqueue.task()
def schedule_browser_view(
    view_name: str,
    username: str,
    site_path: str,
    context_path: str,
    params: dict,
):
    LOG.info(
        f"SCHEDULE {view_name=} {username=} {site_path=}  {context_path=} {params=}"
    )

    ts = time.time()

    t = transaction.manager
    t.begin()
    app = Zope2.app()

    site = app.restrictedTraverse(site_path, None)
    if site is None:
        raise ValueError(f"No site {site_path}")
    setSite(site)
    site = makerequest(site)

    result = None
    with plone.api.env.adopt_user(username=username):
        try:
            try:
                context = site.restrictedTraverse(context_path)
                if context is None:
                    raise ValueError(f"Unknown context {context_path}")
                context = makerequest(context)
                context.REQUEST.form.update(params)

                view = context.restrictedTraverse(view_name, None)
                if view is None:
                    raise ValueError(f"Unknown view {view_name}")

                result = view()
                LOG.info(view_name, result)

                t.commit()
                LOG.debug("Transaction committed")
            except:
                t.abort()
                LOG.error("Transaction aborted", exc_info=True)
                raise
        finally:
            setSite(None)
            app._p_jar.close()

    duration = time.time() - ts
    LOG.debug(f"{duration=}")
    return result
