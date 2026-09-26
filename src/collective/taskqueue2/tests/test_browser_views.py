# -*- coding: utf-8 -*-
import contextlib
import importlib
import io
import json
import logging
import sys
import unittest

from plone import api
from plone.app.testing import TEST_USER_ID, setRoles
from zope.component import getMultiAdapter

from collective.taskqueue2.browser.taskqueue import TaskQueue
from collective.taskqueue2.example.queue_async_task import QueueAsyncTask
from collective.taskqueue2.example.sample_plone_view import (
    ISamplePloneView,
    SamplePloneView,
)
from collective.taskqueue2.testing import COLLECTIVE_TASKQUEUE2_FUNCTIONAL_TESTING


class TaskQueueViewTest(unittest.TestCase):
    layer = COLLECTIVE_TASKQUEUE2_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_view_is_registered(self):
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name="taskqueue-stats"
        )
        self.assertIsInstance(view, TaskQueue)

    def test_stats(self):
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name="taskqueue-stats"
        )
        stats = json.loads(view.stats())
        self.assertEqual(sorted(stats), ["pending", "scheduled"])
        self.assertIsInstance(stats["pending"], int)
        self.assertIsInstance(stats["scheduled"], int)

    def test_stats_via_restricted_traverse(self):
        view = self.portal.restrictedTraverse("@@taskqueue-stats")
        self.assertEqual(sorted(json.loads(view.stats())), ["pending", "scheduled"])


class ExampleViewsTest(unittest.TestCase):
    layer = COLLECTIVE_TASKQUEUE2_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.folder = api.content.create(
            container=self.portal, type="Folder", id="other-folder"
        )

    def test_queue_async_task_example_view(self):
        view = QueueAsyncTask(self.folder, self.portal.REQUEST)
        self.assertIn("Sample View", view())

    def test_sample_plone_view_is_registered(self):
        view = getMultiAdapter(
            (self.folder, self.portal.REQUEST), name="sample-plone-view"
        )
        self.assertIsInstance(view, SamplePloneView)
        self.assertTrue(ISamplePloneView.providedBy(view))

    def test_sample_plone_view_renders(self):
        view = getMultiAdapter(
            (self.folder, self.portal.REQUEST), name="sample-plone-view"
        )
        self.assertIn("other-folder", view())


class HueyClientExampleTest(unittest.TestCase):
    """The example script enqueues one task when it is executed."""

    def test_client_enqueues_a_task(self):
        module_name = "collective.taskqueue2.example.huey_client"
        sys.modules.pop(module_name, None)

        huey_logger = logging.getLogger("huey")
        self.addCleanup(huey_logger.setLevel, huey_logger.level)

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            module = importlib.import_module(module_name)

        self.assertEqual(module.__name__, module_name)
        self.assertEqual(stdout.getvalue().strip(), "added")
