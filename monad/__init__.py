from __future__ import annotations

# from functools import wraps
# from inspect import isgeneratorfunction
from abc import ABC, abstractmethod
import typing as t

Tag = t.TypeVar("Tag")
Val = t.TypeVar("Val")
OtherVal = t.TypeVar("OtherVal")
_BindFn = t.Callable[[Val], "Monad[Tag, OtherVal]"]


_T = t.TypeVar("_T")
_U = t.TypeVar("_U")


def _apply(f: t.Callable[[_T], _U], x: _T) -> _U:
    "Helps a type checker to infer types"
    return f(x)


class Monad(ABC, t.Generic[Tag, Val]):
    @staticmethod
    @abstractmethod
    def unit(value: OtherVal) -> Monad[Tag, OtherVal]:
        ...

    @abstractmethod
    def bind(self, fun: _BindFn[Val, Tag, OtherVal]) -> Monad[Tag, OtherVal]:
        ...

    def __ge__(self, fun: _BindFn[Val, Tag, OtherVal]) -> Monad[Tag, OtherVal]:
        return _apply(self.bind, fun)

    def __rshift__(self, other: Monad[Tag, OtherVal]) -> Monad[Tag, OtherVal]:
        return _apply(self.bind, lambda _: other)

#TODO: use "async def/await" syntax instead of "yield"

# def do(monad_cls) -> Callable[[Any], Any]:
#     """ Limited implementation of the "do" notation """
#
#     if not issubclass(monad_cls, Monad):
#         error = "Wrong type of {}. Must be an instance of Monad"
#         raise TypeError(error.format(monad_cls))
#
#     def wrapper(fun):
#
#         if not isgeneratorfunction(fun):
#             raise ValueError("Function {} must return a generator".format(fun))
#
#         @wraps(fun)
#         def _do(*args, **kwargs):
#             def _next(val):
#                 try:
#                     next_val = gen.send(val)
#                     monad_cls._check_type(next_val)
#                     return next_val.bind(_next)
#                 except StopIteration as e:
#                     return monad_cls._check_type(
#                         e.value
#                     )  # pytype: disable=attribute-error
#
#             gen = fun(*args, **kwargs)
#             val = next(gen)
#             monad_cls._check_type(val)
#             return val.bind(_next)
#
#         return _do
#
#     return wrapper
