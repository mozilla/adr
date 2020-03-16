import os
from collections import Mapping
from pathlib import Path

from appdirs import user_config_dir
from cachy import CacheManager
from cachy.stores import NullStore
from loguru import logger
from tomlkit import parse

import adr


def merge_to(source, dest):
    """
    Merge dict and arrays (override scalar values).

    Keys from source override keys from dest, and elements from lists in source
    are appended to lists in dest.

    Args:
        source (dict): to copy from
        dest (dict): to copy to (modified in place)
    """
    for key, value in source.items():

        if key not in dest:
            dest[key] = value
            continue

        # Merge dict
        if isinstance(value, dict) and isinstance(dest[key], dict):
            merge_to(value, dest[key])
            continue

        if isinstance(value, list) and isinstance(dest[key], list):
            dest[key] = dest[key] + value
            continue

        dest[key] = value

    return dest


def flatten(d, prefix=""):
    if prefix:
        prefix += "."

    result = []
    for key, value in d.items():
        if isinstance(value, dict):
            result.extend(flatten(value, prefix=f"{prefix}{key}"))
        elif isinstance(value, (set, list)):
            vstr = "\n".join([f"    {i}" for i in value])
            result.append(f"{prefix}{key}=\n{vstr}")
        else:
            result.append(f"{prefix}{key}={value}")

    return sorted(result)


class Configuration(Mapping):
    DEFAULT_CONFIG_PATH = Path(user_config_dir("adr")) / "config.toml"
    DEFAULTS = {
        "cache": {"retention": 1440},  # minutes
        "debug": False,
        "debug_url": "https://activedata.allizom.org/tools/query.html#query_id={}",
        "fmt": "table",
        "sources": [os.getcwd(), Path(adr.__file__).parent.parent.as_posix()],
        "url": "http://localhost:5000/query",
        "verbose": False,
    }

    def __init__(self, path=None, config=None):
        self.path = Path(path or os.environ.get("ADR_CONFIG_PATH") or self.DEFAULT_CONFIG_PATH)
        self._config={}
        self.update(self.DEFAULTS)
        if self.path.is_file():
            with open(self.path, "r") as fh:
                content = fh.read()
                self.update(parse(content)["adr"])
        else:
            logger.warning(f"Configuration path {self.path} is not a file.")

    def update(self, config):
        """
        Update the configuration object with new parameters
        :param config: dict of configuration
        """
        for k, v in config.items():
            if v != None:
                self._config[k] = v

        self._config["sources"] = sorted(map(os.path.expanduser, set(self._config["sources"])))

        # Use the NullStore by default. This allows us to control whether
        # caching is enabled or not at runtime.
        self._config["cache"].setdefault("stores", {"null": {"driver": "null"}})
        self.cache = CacheManager(self._config["cache"])
        self.cache.extend("null", lambda driver: NullStore())

    def __len__(self):
        return len(self._config)

    def __iter__(self):
        return iter(self._config)

    def __getitem__(self, key):
        return self._config[key]

    def __getattr__(self, key):
        if key in vars(self):
            return vars(self)[key]
        return self.__getitem__(key)

    def dump(self):
        return "\n".join(flatten(self._config))


config = Configuration()
sources = None
