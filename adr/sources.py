import os
from itertools import chain
from pathlib import Path

from adr import config


class Source:
    def __init__(self, path):
        if path.name.endswith('recipes'):
            self.recipe_dir = Path(path).expanduser().resolve()
            self.query_dir = self.recipe_dir / "queries"
        elif path.name.endswith('queries'):
            self.recipe_dir = None
            self.query_dir = Path(path).expanduser().resolve()
        else:
            print(f"error: {path} is not a valid source!")

        self._recipes = []
        self._queries = []

    @property
    def recipes(self):
        if self._recipes or not self.recipe_dir:
            return self._recipes

        self._recipes = [
            item.stem
            for item in self.recipe_dir.iterdir()
            if item.is_file() and item.stem != "__init__" and item.suffix == ".py"
        ]
        return self._recipes

    @property
    def queries(self):
        if self._queries or not self.query_dir.is_dir():
            return self._queries

        self._queries = [
            item.stem
            for item in self.query_dir.iterdir()
            if item.is_file()
            if item.suffix == ".query"
        ]
        return self._queries


class SourceHandler:
    def __init__(self, sources):
        self._sources = []
        for source in set(sources):
            self.load_source(source)

    def __len__(self):
        return len(self._sources)

    def __getitem__(self, i):
        return self._sources[i]

    def load_source(self, source):
        source = Path(source).expanduser().resolve()

        recipe_dirs = [p for p in source.glob("*recipes") if p.is_dir()]
        query_dirs = [p for p in source.glob("*queries") if p.is_dir()]
        if not (recipe_dirs or query_dirs):
            if source.as_posix() != os.getcwd():
                print(f"warning: {source} does not contain any recipes or queries!")
            return

        for source_dir in recipe_dirs + query_dirs:
            source = Source(source_dir)
            if not (source.recipes or source.queries):
                continue
            self._sources.append(source)

    @property
    def recipes(self):
        return chain(*[s.recipes for s in self._sources])

    @property
    def queries(self):
        return chain(*[s.queries for s in self._sources])

    def _find_source(self, name, query=False):
        sources = self._sources
        if query and "recipe" in config:
            sources = [s for s in sources if config.recipe in s.recipes or not s.recipe_dir]

        attr = "queries" if query else "recipes"

        for s in sources:
            if name in getattr(s, attr):
                return s

    @property
    def active_source(self):
        recipe = config.get("recipe")
        if recipe:
            return self._find_source(recipe)

        query = config.get("query")
        if query:
            return self._find_source(query, query=True)

    def get(self, name, query=False):
        source = self._find_source(name, query=query)
        if source:
            if query:
                return source.query_dir / (name + ".query")
            return source.recipe_dir / (name + ".py")


sources = SourceHandler(config.sources)
