Writing Recipes and Queries
===========================

A "recipe" is composed of several parts:

1. A Python file (the "recipe").
2. One or more Yaml files (the "queries").
3. A context (often built from user input).

Let's take a look at each component in more detail.

Recipes
-------

A ``recipe`` is a Python function that receives context as input, runs one or more ActiveData
queries (passing the context into the query), post-processes the results and returns them in a known
format. For example:

.. code-block:: python

    from adr.query import run_query

    def run(args):
        # The task_durations query returns a list of records of the form:
        # [<task label>, <num tasks run>, <avg runtime>]
        data = run_query('task_durations', args)['data']

        result = []
        for record in data:
            # Sometimes data needs to be sanitized.
            if record[2] is None:
                continue

            record[2] = round(record[2] / 60, 2)  # convert to hours
            record.append(int(round(record[1] * record[2], 0)))  # compute total hours
            result.append(record)

        result = sorted(result, key=lambda k: k[2], reverse=True)
        result.insert(0, ['Taskname', 'Num Jobs', 'Average Hours', 'Total Hours'])
        return result

The above recipe runs the ``task_durations`` query, does a bit of post-processing (e.g sanitizing
data and calculating the total hours), then inserts a header and returns the sorted results.

Logging
~~~~~~~

The ``adr`` runner comes with a logger setup to log to stderr. You can access it like this:

.. code-block:: python

    from loguru import logger

    def run(args):
        logger.info("Starting recipe")

Logging is handled by the `loguru`_ module, and importing ``logger`` will
automatically use the same logging instance that ``adr`` sets up. See that
project's documentation for more details. The default log level is ``INFO`` and
passing in the global ``--verbose`` flag changes the level to
``DEBUG``.

Using Configuration
~~~~~~~~~~~~~~~~~~~

You can access ``adr``'s :class:`configuration <adr.configuration.Configuration>` object like so:

.. code-block:: python

    from adr import config

    def run(args):
        key = str(args)
        if config.cache.has(key):
            value = config.cache.get(key)
        else:
            value = expensive_function(args)
            config.cache.put(key, value)



Queries
-------

A ``query`` is a yaml file representing an `ActiveData query`_ (see here for a quick `yaml
tutorial`_ if you are unfamiliar with the syntax). In the above example, the ``task_durations``
query might look like this:

.. code-block:: yaml

    from: task
    select:
        - {aggregate: count, name: tasks}
        - {aggregate: avg, name: "average minutes", value: {div: {action.duration: 60}}}
    groupby:
        - run.name
    where:
        and:
            - eq: {repo.branch.name: "autoland"}
            - lte: [repo.push.date, {date: "today"}]
            - gte: [repo.push.date, {date: "today-week"}]
            - eq: {build.type: {$eval: build_type}}
            - eq: {run.machine.platform: {$eval: platform}}
    limit: 10000

This query returns the runtimes of all tasks that ran on ``autoland`` over the past week. It
aggregates two values (the number of tasks and average runtime), and groups them by the task label.
So the returned data will look something like:

.. code-block:: json

    {
        "data": [
            ["build-windows10/debug", 413, 68],
            ["build-windows7/pgo", 52, 75],
            "..."
        ]
    }


Inspecting ActiveData
~~~~~~~~~~~~~~~~~~~~~

One of the challenges of writing queries is knowing what tables and attributes exist. The ``adr``
runner comes with a built-in ``inspect`` recipe you can use to see a list of available names:

.. code-block:: bash

    # see available tables
    $ adr inspect
    # see available attributes within a table
    $ adr inspect --table task

You can use ``adr query`` to debug a query while writing it, e.g:

.. code-block:: bash

    $ adr query task_durations -v --format json

For more information on how to compose a query, see ActiveData's `query documentation`_.


Context
-------

Simply writing and running static queries and recipes wouldn't be very interesting. Usually there
are knobs that you'll want to be able to tweak at runtime. For example, you may want to specify a
date range, a specific revision or a task label as an input. To support this, ``adr`` builds a
"context" definition that gets passed into every recipe and query.

In the ``task_duration`` example above, the context is passed into the ``run`` method of the recipe.
The value is an ``argparse.Namespace`` object and values can be accessed with dot notation (e.g
``args.foo``). The context should also be passed into any calls to :func:`~adr.query.run_query`, you can modify it
beforehand if you wish.

But where does this context come from? If you look at the ``task_durations`` query, you'll notice
two ``$eval`` statements (for ``build_type`` and ``platform``). This is a `JSON-e`_ directive that
substitutes the associated name with the corresponding value in the context definition.


Context Discovery
~~~~~~~~~~~~~~~~~

The ``adr`` runner will automatically scan your recipe and try to determine which queries it
depends on. It will then read those queries and find all of the context values that ``JSON-e`` is
expecting. The ``adr`` runner will also scan your recipe for attribute access on the ``args``
object. For example, if you use ``args.foo`` in your recipe, ``adr`` will know to supply the ``foo``
context to your recipe.


Defining Context
~~~~~~~~~~~~~~~~

But just knowing that a recipe uses a particular context value isn't enough, that value needs to
actually be defined somewhere. There are three locations you can define context:

1. The easiest (and recommended) place to define context is in a shared ``context.yml`` file. This
   option is useful when you have many recipes/queries that need to use the same context definition
   over and over.  It lives in the same directory as the recipes that use it. For example:

.. code-block:: yaml

    foo:
        flags: ["-f", "--foo"]
        dest: "foo"
        action: "store_true"
        default: false
        help: "Store true in the 'foo' context"

2. Context can also be defined in the query itself. This is useful when you want to tweak knobs when
   running standalone queries (e.g with ``adr query``). This method is also nice because it keeps
   the definition close the usage of the context. These go in an extra ``context`` key:

.. code-block:: yaml

    from: task
    ...
    context:
        foo:
            flags: ["-f", "--foo"]
            dest: "foo"
            action: "store_true"
            default: false
            help: "Store true in the 'foo' context"

   This context key will be removed from the query before it gets submitted to ActiveData.

3. Finally, context can live in recipe itself. This is only for context that is used directly by the
   recipe, queries won't be able to discover context defined here. As such, this method isn't
   typically recommended. These go in the ``RUN_CONTEXTS`` global variable, e.g:

.. code-block:: python

    from adr.query import run_query

    RUN_CONTEXTS = [
        {
            "foo": {
                "flags": ["-f", "--foo"],
                "dest": "foo",
                "action": "store_true",
                "default": False,
                "help": "Store true in the 'foo' context"
            }
        }
    ]

    def run(args):
        assert hasattr(args, 'foo')
        ...

   Note that the context definitions mirror the arguments to
   ``argparse.ArgumentParser.add_argument``.


When the ``adr`` runner determines that your recipe uses a given context value, it will search all
three locations. If no context matching the name was found an exception is raised. In most cases,
just defining the context in ``context.yml`` will accomplish what you want.


Overriding Shared Context
~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes a recipe may wish to override a context, for example maybe a recipe wants to use a
different default value. This is possible via the :func:`~adr.context.override` function:

.. code-block:: python

    from adr.context import override

    RUN_CONTEXTS = [
        override('branch', default="mozilla-beta"),
    ]

This will only modify the default value of the ``branch`` context, leaving the rest as is.


Project Structure
-----------------

Now that we're somewhat familiar with the various components, let's take a look at how they all tie
together in a project repository:

.. code-block:: text

    - project root
        - recipes
            - my_recipe_1.py
            - my_recipe_2.py
            - context.yml
            - queries
                - my_query_1.yml
                - my_query_2.yml

Typically it's recommend to invoke the ``adr`` runner from the project root. This is because it will
always implicitly search all directories that end with "recipes" in the $CWD. So ``recipes``,
``ci_recipes`` and ``perf_recipes`` are all valid directory names. Your project can even have
multiple directories containing recipes if you wish.

Within the "recipe dir", you'll find the recipe files, the optional context.yml and a ``queries``
directory for all of the query files.


Creating a New Project
----------------------

Creating a new recipe project isn't trivial, especially if you want to have tests, documentation,
CI, etc. To make the initial setup a bit easier, there is a `cookiecutter`_ repository for setting
up new "recipe projects".

See the `README`_ for more information, but the gist is you can run:

.. code-block:: bash

    $ pip install cookiecutter
    $ cookiecutter https://github.com/ahal/cookiecutter-active-data-recipes

This will guide you through a wizard to help set up your project.


.. _loguru: https://github.com/Delgan/loguru
.. _ActiveData query: https://github.com/mozilla/ActiveData/blob/dev/docs/jx.md
.. _yaml tutorial: https://gettaurus.org/docs/YAMLTutorial/
.. _query documentation: https://github.com/mozilla/ActiveData/blob/dev/docs/jx.md
.. _JSON-e: https://taskcluster.github.io/json-e/
.. _cookiecutter: https://github.com/audreyr/cookiecutter
.. _README: https://github.com/ahal/cookiecutter-active-data-recipes
