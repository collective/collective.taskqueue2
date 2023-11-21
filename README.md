# collective.taskqueue2


A taskqueue implementation for Plone 5/6 based on the Huey package.

See https://huey.readthedocs.io/en/latest/


## Features

- Can be bullet points


## Installation

Install collective.taskqueue2 by adding it to your buildout::

    [buildout]

    ...

    eggs =
        collective.taskqueue2


and then running ``bin/buildout``

## Configuration

### Environment Variables

The code relies on the `HUEY_TASKQUEUE_URL` environment variable to determine the configuration of the task queue. If the environment variable is not set, it falls back to a default value (`sqlite:///tmp/huey_queue.sqlite`). The `HUEY_TASKQUEUE_URL` should be set as a string representing the URL of the task queue configuration.

To use the code with different task queue configurations, you can set the `HUEY_TASKQUEUE_URL` environment variable with a URL representing the desired configuration. Here are some examples of URL formats for different configurations:

- SQLite: `HUEY_TASKQUEUE_URL=sqlite:///path/to/database.sqlite`
- Redis: `HUEY_TASKQUEUE_URL=redis://localhost:6379/0`
- Memory: `HUEY_TASKQUEUE_URL=memory://`
- File: `HUEY_TASKQUEUE_URL=file:///path/to/queue/folder`

Make sure to adjust the URLs according to your specific environment.

### Examples

Here are examples of different URL configurations for each supported scheme:

1. SQLite:

   `HUEY_TASKQUEUE_URL=sqlite:///path/to/database.sqlite`

   This URL configures the task queue to use SQLite with a specific database file.

2. Redis:

   `HUEY_TASKQUEUE_URL=redis://localhost:6379/0`

   This URL configures the task queue to use Redis with a specific host (`localhost`), port (`6379`), and database (`0`).

3. Memory:

   `HUEY_TASKQUEUE_URL=memory://`

   This URL configures the task queue to use an in-memory storage. No additional parameters are needed.

4. File:

   `HUEY_TASKQUEUE_URL=file:///path/to/queue/folder`

   This URL configures the task queue to use a file-based storage with a specific folder path.

Ensure that you set the appropriate URL corresponding to the desired scheme before running the code.

The `huey_taskqueue` object created based on the URL configuration can be used further in the application for task queuing and processing.


## Authors

 - Andreas Jung <info@zopyx.com> for University of Bologna



## Contribute

- Issue Tracker: https://github.com/collective/collective.taskqueue2/issues
- Source Code: https://github.com/collective/collective.taskqueue2
- Documentation: https://docs.plone.org/foo/bar



## License

The project is licensed under the GPLv2.
