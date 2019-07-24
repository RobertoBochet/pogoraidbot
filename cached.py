import functools
from typing import Callable


class Cached:
    def __init__(self, func: Callable):
        self.func = func
        self.cached = False
        self.cache = None

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)

    def __call__(self, *args, **kwargs):
        if self.cached:
            return self.cache

        self.cache = self.func(*args, **kwargs)
        self.cached = True

        return self.cache
