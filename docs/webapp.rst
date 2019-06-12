Web Application
===============

The ``adr`` library comes with a built-in web application which can be used as an alternative
frontend to the cli. You can spin it up from the root of your recipe project using:

.. code-block:: bash

    $ adr-app

No changes to your recipes are needed for them to be supported.

URL Parameters
--------------

The context is encoded as URL parameters. For example, if you are serving the app on localhost and
have a ``task_durations`` recipe that takes a ``platform`` context, you can load the query with
``http://localhost:5000/task_durations?platform=linux``. This makes sharing queries much easier.

Caching
-------

As with the cli, query results can be cached by the server. See the :ref:`caching configuration
<cache>` for more details.
