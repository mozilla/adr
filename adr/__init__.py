def configure(config_):
    """
    INJECT CONFIGURATION INTO ADR
    :param config_:  dict of configuration
    """
    from adr import configuration

    configuration.config = configuration.Configuration(config=config_)
    for s in configuration.config.sources:
        configuration.sources.load_source(s)

