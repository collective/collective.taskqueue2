# -*- coding: utf-8 -*-

# from collective.taskqueue2 import _
from plone.dexterity.browser.view import DefaultView
from zope.interface import implementer
from zope.interface import Interface


# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ISamplePloneView(Interface):
    """Marker Interface for ISamplePloneView"""


@implementer(ISamplePloneView)
class SamplePloneView(DefaultView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('sample_plone_view.pt')

    def __call__(self):
        # Implement your own actions:
        return super(SamplePloneView, self).__call__()
