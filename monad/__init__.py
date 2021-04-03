from __future__ import annotations

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

    def __rshift__(
        self: Monad[Tag, None], other: Monad[Tag, OtherVal]
    ) -> Monad[Tag, OtherVal]:
        return _apply(self.bind, lambda _: other)

    def __iter__(self: Monad[Tag, Val]) -> t.Generator[Monad[Tag, Val], None, Val]:
        val = yield self
        return t.cast(Val, val)


DoBlock = t.Generator[Monad[Tag, t.Any], None, Monad[Tag, Val]]


def do(generator: DoBlock[Tag, Val]) -> Monad[Tag, Val]:
    """ Limited implementation of the "do" notation """

    def _next(val: t.Any) -> t.Any:
        try:
            next_val = generator.send(val)
            return next_val.bind(_next)
        except StopIteration as e:
            return e.value

    val = next(generator)
    return val.bind(_next)
