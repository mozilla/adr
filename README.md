[![Build Status](https://travis-ci.org/mozilla/active-data-recipes.svg?branch=master)](https://travis-ci.org/mozilla/active-data-recipes)
[![PyPI version](https://badge.fury.io/py/adr.svg)](https://badge.fury.io/py/adr)
[![PyPI version](https://readthedocs.org/projects/active-data-recipes/badge/?version=latest)](https://active-data-recipes.readthedocs.io)

# adr

This is the runner for [ActiveData recipes][0], it provides a command line interface and flask web
app. [ActiveData][4] is a large data warehouse containing billions of records related to Mozilla's
CI, version control, bug tracking and much more. An ActiveData "recipe" is a Python snippet that
runs one or more queries against ActiveData, then performs some post-processing before returning the
results.

Other than a handful of built-in recipes, this repo doesn't contain any actual recipes itself. Those
live in project specific repositories that will typically depend on some version of this library.
The recommended way to run a recipe is to follow the README of the desired recipe project rather
than starting here.


# Known Recipe Projects

Here are some of the known repositories containing ActiveData recipes:

* [active-data-recipes][3] - Misc recipes that are mostly untriaged. Good for finding examples to
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

To contribute to `active-data-recipes` first [install poetry][2], then run:

    $ git clone https://github.com/mozilla/active-data-recipes
    $ cd active-data-recipes
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

[0]: https://active-data-recipes.readthedocs.io
[1]: https://active-data-recipes.readthedocs.io/en/latest/recipes.html
[2]: https://poetry.eustace.io/docs/#installation
[3]: https://github.com/mozilla/active-data-recipes
[4]: https://github.com/mozilla/ActiveData
