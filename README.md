[![Build Status](https://travis-ci.org/mozilla/adr.svg?branch=master)](https://travis-ci.org/mozilla/adr)
[![PyPI version](https://badge.fury.io/py/adr.svg)](https://badge.fury.io/py/adr)
[![PyPI version](https://readthedocs.org/projects/active-data-recipes/badge/?version=latest)](https://active-data-recipes.readthedocs.io)

# adr

This is the runner for [ActiveData recipes][0], it provides a command line interface and flask web
app. [ActiveData][1] is a large data warehouse containing billions of records related to Mozilla's
CI, version control, bug tracking and much more. An ActiveData "recipe" is a Python snippet that
runs one or more queries against ActiveData, then performs some post-processing before returning the
results.

Other than a handful of built-in recipes, this repo doesn't contain any actual recipes itself. Those
live in project specific repositories that will typically depend on some version of this library.
The recommended way to run a recipe is to follow the README of the desired recipe project rather
than starting here.


# Known Recipe Projects

Here are some of the known repositories containing ActiveData recipes:

* [active-data-recipes][2] - Misc recipes that are mostly untriaged. Good for finding examples to
  copy from.


# Installation

Although installing `adr` directly is not recommended, it is still supported:

    $ pip install adr

You will need Python 3.6 or higher.


# Usage

The `adr` binary will search for recipes that live under $CWD, so usually just changing directories
to the repository containing recipes is the best way to ensure `adr` can discover them.

For a list of available recipes:

    $ adr --list

To run a given recipe:

    $ adr <recipe> <options>

For recipe specific options see:

    $ adr <recipe> -- --help


# Contributing

To contribute to `adr` first [install poetry][3], then run:

    $ git clone https://github.com/mozilla/adr
    $ cd adr
    $ poetry install

Now you can use `poetry run` to perform various development commands:

    # run adr
    $ poetry run adr <recipe>

    # run webapp
    $ poetry run adr-app

    # run tests
    $ poetry run tox

Alternatively activate the `poetry` shell ahead of time:

    $ poetry shell

    # run adr
    $ adr <recipe>

    # run app
    $ adr-app

    # run tests
    $ tox

# Windows Install and Development

If you wish to run tests in your IDE, or if you find [Poetry does not work](https://github.com/python-poetry/poetry/issues/2244), you can export-and-install manually:


We will be locking the version numbers of the project requirements, so it is best to setup a virtual environment:

    c:\Python37\python.exe -m venv venv
    venv\Scripts\activate

Poetry can export the requirements

    poetry export -f requirements.txt > requirements.in   

...unfortunately, the exported requirements includes version conflicts, preventing install.  We use `pip-tools` to fix that:   

    python -m pip install pip-tools
    pip-compile --upgrade --generate-hashes --output-file requirements.txt requirements.in
    pip install -r requirements.txt
    
A few more libraries are required to run the tests

    pip install wheel
    pip install responses
    pip install flask
    
Finally, we can run the tests.

    pytest -v test


[0]: https://active-data-recipes.readthedocs.io
[1]: https://github.com/mozilla/ActiveData
[2]: https://github.com/mozilla/active-data-recipes
[3]: https://poetry.eustace.io/docs/#installation
