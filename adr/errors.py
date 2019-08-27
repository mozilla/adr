class MissingDataError(ValueError):
    """ Raised when a query returns no data.
    """

    pass


class RecipeException(Exception):
    """ Raised when there are errors in the recipe
        when running it
    """

    pass
