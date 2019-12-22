import functools
from typing import Callable


class CachedMethod:
    def __init__(self, func: Callable):
        self.func = func

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)

    def __call__(self, *args, **kwargs):
        inst = args[0]
        func_name = self.func.__name__

        try:
            inst.__cache__
        except AttributeError:
            inst.__cache__ = {}

        try:
            return inst.__cache__[func_name]
        except KeyError:
            pass

        inst.__cache__[func_name] = self.func(*args, **kwargs)

        return inst.__cache__[func_name]
