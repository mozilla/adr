from __future__ import absolute_import, print_function

import collections
import imp
from argparse import Namespace
from pathlib import Path

from docutils.core import publish_parts
from loguru import logger

from adr import config, context, sources
from adr.context import RequestParser
from adr.errors import MissingDataError, RecipeException
from adr.formatter import all_formatters
from adr.query import load_query_context

here = Path(__file__).parent.resolve()


def get_module(recipe):
    """
    Get module of a recipe
    Args:
        recipe (str): name of recipe
    :return: module
    """
    path = sources.get(recipe)
    return imp.load_module(f"recipes.{path.stem}", *imp.find_module(recipe, [path.parent]))


def get_recipe_contexts(recipe):
    """
    Extract list of recipe context definition from the recipe file and related query files
    Args:
        recipe (str): name of recipe
    Returns:
        result (dict): definition of all contexts needed for recipe
    """
    mod = get_module(recipe)

    # try to extract name of query and run contexts automatically from run function
    queries, run_contexts = context.extract_arguments(mod.run, "run_query")

    specific_contexts = collections.OrderedDict()
    if hasattr(mod, "RUN_CONTEXTS"):
        context_info = mod.RUN_CONTEXTS
        for item in context_info:
            specific_contexts.update(item)

    # get full definition of all contexts needed for recipe
    recipe_context_def = collections.OrderedDict()
    for query_name in set(queries):
        query_context_def = load_query_context(query_name)
        recipe_context_def.update(query_context_def)

    run_context_def = context.get_context_definitions(run_contexts, specific_contexts)
    recipe_context_def.update(run_context_def)

    return recipe_context_def


def run_recipe(recipe, args, from_cli=True):
    """Given a recipe, calls the appropriate query and returns the result.

    The provided recipe name is used to make a call to the modules.

    Args:
        recipe (str): name of the recipe to be run.
        args (list): remainder arguments that were unparsed.
        from_cli (bool): true if run recipe from cli
    Returns:
        output (str): output after formatted.

    """
    formatted_args = ""
    if args:
        formatted_args += f" with args: {args}"
    logger.debug(f"Running recipe {recipe}{formatted_args}")

    recipe_context_def = get_recipe_contexts(recipe)

    if from_cli:
        doc = get_docstring(recipe, fmt="text")
        parser = RequestParser(recipe_context_def, prog="adr {}".format(recipe), description=doc)
        parsed_args = vars(parser.parse_args(args))
    else:
        parsed_args = args

    try:
        mod = get_module(recipe)
        output = mod.run(Namespace(**parsed_args))
        if output is None:
            raise RecipeException()
    except MissingDataError:
        return "ActiveData didn't return any data."
    except RecipeException:
        return ("The query has successfully returned but no data is available for"
                "formatting. Does your run function have a return statement")

    if isinstance(config.fmt, str):
        fmt = all_formatters[config.fmt]

    return fmt(output)


def get_docstring(recipe, fmt="html"):
    """
    Get docstring of a recipe
    Args:
        recipe (str): name of recipe
        fmt (str): Format to return docstring (default: 'html')
    Result:
        html or text (transformed from rst)
    """
    assert fmt in ("html", "text")
    doc = get_module(recipe).__doc__

    if fmt == "html":
        return publish_parts(doc, writer_name="html")["html_body"]

    # TODO Figure out how to use Sphinx's TextWriter with publish_parts.
    lines = doc.splitlines()
    delete = []
    for i, line in enumerate(lines[:]):
        if not line.startswith(".. "):
            continue

        delete.append(i)
        if not lines[i - 1]:
            delete.append(i - 1)

    for d in sorted(delete, reverse=True):
        del lines[d]

    return "\n".join(lines)


def is_fail(recipe):
    mod = get_module(recipe)
    return getattr(mod, "BROKEN", False)
