# bin/instance run scripts/huey_consumer.py

import logging
import time

import plone.api
import transaction
import Zope2
from Testing.makerequest import makerequest
from zope.component.hooks import setSite

from huey import crontab 

# Start huey consumer as thread

from collective.taskqueue2.huey_logger import LOG
from collective.taskqueue2.huey_config import huey_taskqueue

@huey_taskqueue.on_startup()
def on_startup():
    LOG.info("ON STARTUP")


@huey_taskqueue.pre_execute()
def pre_execute_hook(task):
    LOG.info(f"PRE HOOK: {task}")


@huey_taskqueue.post_execute()
def post_execute_hook(task, task_value, exc):
    LOG.info(f"POST HOOK {task=} {task_value=} {exc=}")



@huey_taskqueue.periodic_task(crontab(minute='*', hour='*'))
def periodic_example():
    LOG.info("PERIODIC TASK")


@huey_taskqueue.task()
def schedule_browser_view(
    view_name: str,
    username: str,
    site_path: str,
    context_path: str,
    params: dict,
):
    LOG.info(f"SCHEDULE {view_name=} {username=} {site_path=}  {context_path=} {params=}")

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
                LOG.info("transaction-commit")
            except:
                t.abort()
                LOG.info("transaction-abort")
                raise
        finally:
            setSite(None)
            app._p_jar.close()

    duration = time.time() - ts
    LOG.info(f"{duration=}")
    return result
