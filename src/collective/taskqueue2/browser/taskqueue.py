from ..huey_config import huey_taskqueue
from Products.Five import BrowserView

import json


class TaskQueue(BrowserView):
    def stats(self):
        """Return taskqueue stats"""
        r = dict(
            pending=len(huey_taskqueue.pending()),
            scheduled=len(huey_taskqueue.scheduled()),
        )
        return json.dumps(r)
