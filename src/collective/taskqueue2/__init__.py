# -*- coding: utf-8 -*-
"""Init and utils."""
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('collective.taskqueue2')

from collective.taskqueue2 import huey_consumer
