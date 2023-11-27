# -*- coding: utf-8 -*-
from collective.taskqueue2 import _
from collective.taskqueue2.interfaces import ICollectiveTaskqueue2Layer
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.restapi.controlpanels import RegistryConfigletPanel
from plone.z3cform import layout
from zope import schema
from zope.component import adapter
from zope.interface import Interface


class ITaskqueueControlpanel(Interface):
    myfield_name = schema.TextLine(
        title=_(
            "This is an example field for this control panel",
        ),
        description=_(
            "",
        ),
        default="",
        required=False,
        readonly=False,
    )


class TaskqueueControlpanel(RegistryEditForm):
    schema = ITaskqueueControlpanel
    schema_prefix = "collective.taskqueue2.taskqueue_controlpanel"
    label = _("Taskqueue Controlpanel")


TaskqueueControlpanelView = layout.wrap_form(
    TaskqueueControlpanel, ControlPanelFormWrapper
)


@adapter(Interface, ICollectiveTaskqueue2Layer)
class TaskqueueControlpanelConfigletPanel(RegistryConfigletPanel):
    """Control Panel endpoint"""

    schema = ITaskqueueControlpanel
    configlet_id = "taskqueue_controlpanel-controlpanel"
    configlet_category_id = "Products"
    title = _("Taskqueue Controlpanel")
    group = ""
    schema_prefix = "collective.taskqueue2.taskqueue_controlpanel"
