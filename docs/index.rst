.. ActiveData Recipes documentation master file, created by
   sphinx-quickstart on Thu Sep 13 10:32:04 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ActiveData Recipes
==================

ActiveData_ is a data warehouse operated by Mozilla. It ingests data from many sources, such as
`Taskcluster`_, `Treeherder`_, Mercurial, Logs, Bugzilla, and contains many billions of records.
Due to the sheer size and complexity of ActiveData, using it to answer everyday questions is not a
straightforward task and the built-in `query tool`_ is often insufficient.

The ``active-data-recipes`` project was created to provide an intuitive way to not only use
ActiveData, but to save your queries for future use and share them with others. The project consists
of two main parts:

    1. A series of ``recipe collections`` (typically structured in their own repository somewhere).
    2. The `adr`_ runner, which is packaged as a library that recipe collections depend on.

For more information on how to use the ``adr`` binary to run recipes, see the :doc:`usage
documentation <usage>`.

.. _ActiveData: https://github.com/mozilla/ActiveData
.. _Taskcluster: https://docs.taskcluster.net/docs
.. _Treeherder: https://treeherder.mozilla.org
.. _query tool: https://activedata.allizom.org/tools/query.html
.. _adr: https://github.com/mozilla/adr

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage
   webapp
   writing
   recipes
   api/modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
