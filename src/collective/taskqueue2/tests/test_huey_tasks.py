# -*- coding: utf-8 -*-
import json
import unittest
from unittest import mock

from plone import api
from plone.app.testing import TEST_USER_ID, setRoles
import transaction
from zope.component.hooks import getSite, setSite

from collective.taskqueue2 import huey_tasks
from collective.taskqueue2.huey_tasks import (
    dump_queue_stats,
    on_startup,
    post_execute_hook,
    pre_execute_hook,
    schedule_browser_view,
)
from collective.taskqueue2.testing import COLLECTIVE_TASKQUEUE2_FUNCTIONAL_TESTING


QUEUE_USER = "queue-user"
QUEUE_USER_EMAIL = "queue-user@example.com"


class HueyTasksTest(unittest.TestCase):
    layer = COLLECTIVE_TASKQUEUE2_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal_path = "/".join(self.portal.getPhysicalPath())
        # schedule_browser_view adopts the given username, so the user has to
        # exist in a user folder of the portal. adopt_user() resolves it via
        # acl_users.getUser(), i.e. by the login name.
        member = api.user.create(
            username=QUEUE_USER,
            email=QUEUE_USER_EMAIL,
            password="th3-qu3u3-s3cr3t",
            roles=["Manager"],
        )
        self.queue_user = member.getUserName()
        # The task opens its own ZODB connection (Zope2.app()), and
        # transaction.manager.begin() aborts an open transaction - so the
        # fixtures have to be committed before the task runs.
        transaction.commit()

    def schedule(self, **kwargs):
        params = {
            "view_name": "@@taskqueue-stats",
            "username": self.queue_user,
            "site_path": self.portal_path,
            "context_path": self.portal_path,
            "params": {},
        }
        params.update(kwargs)
        site = getSite()
        try:
            return schedule_browser_view.call_local(**params)
        finally:
            # the task resets the site to None when it is done
            setSite(site)

    def test_startup_and_execute_hooks(self):
        on_startup()
        pre_execute_hook(None)
        post_execute_hook(None, None, None)

    def test_dump_queue_stats(self):
        with self.assertLogs("huey", level="INFO") as cm:
            dump_queue_stats.call_local()
        self.assertIn("Taskqueue stats", cm.output[0])

    def test_all_tasks_use_the_configured_queue(self):
        self.assertIs(schedule_browser_view.huey, huey_tasks.huey_taskqueue)
        self.assertIs(dump_queue_stats.huey, huey_tasks.huey_taskqueue)

    def test_schedule_browser_view_returns_the_view_result(self):
        result = self.schedule(params={"foo": "bar"})
        self.assertEqual(sorted(json.loads(result)), ["pending", "scheduled"])

    def test_schedule_browser_view_with_unknown_site(self):
        with self.assertRaisesRegex(ValueError, "No site"):
            self.schedule(site_path="/does-not-exist")

    def test_schedule_browser_view_with_unknown_view(self):
        with self.assertLogs("huey", level="ERROR") as cm:
            with self.assertRaisesRegex(ValueError, "Unknown view"):
                self.schedule(view_name="@@does-not-exist")
        self.assertIn("Transaction aborted", cm.output[0])

    def test_schedule_browser_view_with_unknown_context(self):
        fake_site = mock.MagicMock()
        fake_site.restrictedTraverse.return_value = None
        with mock.patch.object(huey_tasks, "makerequest", return_value=fake_site):
            with self.assertLogs("huey", level="ERROR") as cm:
                with self.assertRaisesRegex(ValueError, "Unknown context"):
                    self.schedule()
        self.assertIn("Transaction aborted", cm.output[0])
