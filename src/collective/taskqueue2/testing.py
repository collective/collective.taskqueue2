# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.taskqueue2


class CollectiveTaskqueue2Layer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity
        self.loadZCML(package=plone.app.dexterity)
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=collective.taskqueue2)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.taskqueue2:default')


COLLECTIVE_TASKQUEUE2_FIXTURE = CollectiveTaskqueue2Layer()


COLLECTIVE_TASKQUEUE2_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_TASKQUEUE2_FIXTURE,),
    name='CollectiveTaskqueue2Layer:IntegrationTesting',
)


COLLECTIVE_TASKQUEUE2_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_TASKQUEUE2_FIXTURE,),
    name='CollectiveTaskqueue2Layer:FunctionalTesting',
)


COLLECTIVE_TASKQUEUE2_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_TASKQUEUE2_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='CollectiveTaskqueue2Layer:AcceptanceTesting',
)
