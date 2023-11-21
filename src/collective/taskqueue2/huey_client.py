# bin/instance run scripts/huey_client.py

from datetime import datetime

import logging


#
logging.getLogger("huey").setLevel(logging.DEBUG)

from collective.taskqueue2.huey_tasks import schedule_browser_view


now = datetime.now().isoformat()
schedule_browser_view(
    view_name="debug-demo-view",
    context_path="/magazine",
    site_path="/magazine",
    username="admin",
    params=dict(foo="bar", bar="foo", meaning_of_life=42, now=now),
)
print("added")
