import functools


class Cached:
    def __init__(self, func):
        self.func = func
        self.cached = False

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)

    def __call__(self, *args, **kwargs) -> bool:
        if self.cached:
            return self.cache

        self.cache = self.func(*args, **kwargs)
        self.cached = True

        return self.cache
