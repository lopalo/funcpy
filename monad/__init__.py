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
