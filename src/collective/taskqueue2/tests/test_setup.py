# -*- coding: utf-8 -*-
import unittest

from plone.base.interfaces import INonInstallable
from plone.base.utils import get_installer
from plone.browserlayer.utils import registered_layers
from zope.component import queryUtility
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from collective.taskqueue2.interfaces import ICollectiveTaskqueue2Layer
from collective.taskqueue2.setuphandlers import HiddenProfiles, post_install, uninstall
from collective.taskqueue2.testing import COLLECTIVE_TASKQUEUE2_INTEGRATION_TESTING


class SetupTest(unittest.TestCase):
    layer = COLLECTIVE_TASKQUEUE2_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

    def test_addon_is_installed(self):
        installer = get_installer(self.portal)
        self.assertTrue(installer.is_product_installed("collective.taskqueue2"))

    def test_browser_layer_is_registered(self):
        self.assertIn(ICollectiveTaskqueue2Layer, registered_layers())

    def test_browser_layer_extends_the_default_layer(self):
        self.assertTrue(ICollectiveTaskqueue2Layer.isOrExtends(IDefaultBrowserLayer))

    def test_hidden_profiles(self):
        hidden = HiddenProfiles()
        self.assertEqual(
            hidden.getNonInstallableProfiles(),
            ["collective.taskqueue2:uninstall"],
        )
        self.assertEqual(
            hidden.getNonInstallableProducts(),
            ["collective.taskqueue2.upgrades"],
        )

    def test_hidden_profiles_utility_is_registered(self):
        utility = queryUtility(
            INonInstallable, name="collective.taskqueue2-hiddenprofiles"
        )
        self.assertIsInstance(utility, HiddenProfiles)

    def test_post_install_and_uninstall(self):
        post_install(self.portal)
        uninstall(self.portal)
