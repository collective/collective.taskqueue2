# Test suite of collective.taskqueue2.
#
# The package must not depend on an external Redis, nor on the queue database
# in /tmp that is used as the production default. This is set here, in the
# first module the test runner imports, because the Huey instance is created
# while the production modules are imported.
import os


os.environ.setdefault("HUEY_TASKQUEUE_URL", "memory://")
