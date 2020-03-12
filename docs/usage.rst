Command Line Usage
==================

Installation
------------

Typically installing the ``adr`` package directly is not recommended. Instead try to follow the
instructions from the recipe project's README. This usually involves installing the project into a
virtualenv.

But if you have multiple recipe collections on the go (and don't want to deal with switching
virtualenvs), or if your recipe collection isn't structured as a package with dependencies, you can
always install ``adr`` manually:

.. code-block:: bash

    $ pip install adr

.. warning::

    If installing ``adr`` manually the version that gets installed might not be compatible with the
    recipes you are trying to run. That's why structuring recipes as a package that depend on
    ``adr`` and then installing the recipe collection is preferred.


Running Recipes
---------------

Once you've installed the recipe project (or installed ``adr`` manually), change to the recipe
project's root. You can list the available recipes like this:

.. code-block:: bash

    $ cd <path/to/recipe/project>
    $ adr list

Then run a recipe like this:

.. code-block:: bash

    $ adr <recipe>

Most recipes will have some command line arguments that change how the recipe behaves. For example,
imagine a ``push_hours`` recipe that returns the number of compute hours spent on a given push.
Such a recipe might have a ``--rev`` argument to specify which revision to query:

.. code-block:: bash

    $ adr push_hours --help         # see recipe help
    $ adr push_hours --rev <rev>    # run recipe on <rev>


Configuration
-------------

The ``adr`` binary looks for a configuration file in your user config dir (e.g
``~/.config/adr/config.toml``):

.. code-block:: bash

    $ adr config      # view active configuration
    $ adr config -e   # edit config file

The config is a `TOML`_ file, which looks something like:

.. code-block:: toml

    [adr]
    verbose = true
    fmt = "json"


List of Options
~~~~~~~~~~~~~~~

The following keys are valid config options.

cache
`````
This value allows you to set up a cache to store the results of queries for future use. This
avoids the penalty of hitting ActiveData and is especially useful when writing new recipes or when
the result of a query is not expected to change.

The ``adr`` module uses `cachy`_ to handle caching. Therefore the following stores are supported:

* database
* file system
* memcached
* redis

To enable caching, you'll need to configure at least one store using the ``cache.stores`` key.
Follow `cachy's configuration format`_ identically. In addition to the options ``cachy`` supports,
you can set the ``adr.cache.retention`` key to the time in minutes before stored queries are
invalidated.

For example:

.. code-block:: toml

    [adr.cache]
    retention = 10080  # minutes

    [adr.cache.stores]
    file = { driver = "file", path = "/path/to/dir/to/keep/cache" }

In addition, ``adr`` provides a ``seeded-file`` store. This is the same as the "file system" store,
except you can specify a URL to initially seed your cache on creation:

.. code-block:: toml

    [adr.cache.stores]
    file = {
        driver = "seeded-file",
        path = "/path/to/dir/to/keep/cache",
        url = "https://example.com/adr_cache.tar.gz"
    }

Supported archive formats include ``.zip``, ``.tar``, ``.tar.gz``, ``.tar.bz2`` and ``.tar.zst``.

The config also accepts a ``reseed_interval`` (in minutes) which will re-seed the cache after the
interval expires. This assumes the URL is automatically updated by some other process.

As well as an ``archive_relpath`` config, which specifies the path to the cache data "within" the
archive. Otherwise the cache data is assumed to be right at the root of the archive.

fmt
```

The format to output results in (default: ``table``). Valid options are:

* json
* markdown
* table
* tab


sources
```````

A list of paths to search for recipes. Built-in recipes and the current working directory are
implicitly searched, so this is only necessary if you want to run recipes from outside of the
project root.

For example:

.. code-block:: toml

    [adr]
    sources = [
        "/path/to/my/first/recipe/project",
        "/path/to/my/other/recipes",
    ]


url
```

Url of the ActiveData endpoint to query (default: ``https://activedata.allizom.org/query``)


verbose
```````

Enable verbose mode (default: ``false``). This enables debug logging which includes a JSON
representation of every query submitted to ActiveData (which can be pasted into the ActiveData
`query tool`_).


.. _TOML: https://github.com/toml-lang/toml
.. _cachy: https://cachy.readthedocs.io/en/latest/
.. _cachy's configuration format: https://cachy.readthedocs.io/en/latest/configuration.html#
.. _query tool: https://activedata.allizom.org/tools/query.html
