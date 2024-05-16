# -*- coding: utf-8 -*-
from collective.taskqueue2.testing import COLLECTIVE_TASKQUEUE2_FUNCTIONAL_TESTING
from collective.taskqueue2.testing import COLLECTIVE_TASKQUEUE2_INTEGRATION_TESTING
from collective.taskqueue2.views.sample_plone_view import ISamplePloneView
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter
from zope.interface.interfaces import ComponentLookupError

import unittest


class ViewsIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_TASKQUEUE2_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        api.content.create(self.portal, "Folder", "other-folder")
        api.content.create(self.portal, "Document", "front-page")

    def test_sample_plone_view_is_registered(self):
        view = getMultiAdapter(
            (self.portal["other-folder"], self.portal.REQUEST), name="sample-plone-view"
        )
        self.assertTrue(ISamplePloneView.providedBy(view))

    def test_sample_plone_view_not_matching_interface(self):
        view_found = True
        try:
            view = getMultiAdapter(
                (self.portal["front-page"], self.portal.REQUEST),
                name="sample-plone-view",
            )
        except ComponentLookupError:
            view_found = False
        else:
            view_found = ISamplePloneView.providedBy(view)
        self.assertFalse(view_found)


class ViewsFunctionalTest(unittest.TestCase):

    layer = COLLECTIVE_TASKQUEUE2_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
