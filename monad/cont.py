from __future__ import annotations
import typing as t
from . import Monad as BaseMonad, Val, OtherVal


R = t.TypeVar("R")


@t.final
class _Cont(t.Generic[R]):
    "Type tag that makes 'Cont' monad compatible only with itself"
    pass


_Monad = BaseMonad[_Cont[R], Val]
_BindFn = t.Callable[[Val], BaseMonad[_Cont[R], OtherVal]]
_C = t.Callable[[Val], R]
_ContFn = t.Callable[[_C[Val, R]], R]


class Cont(_Monad[R, Val]):
    def __init__(self, fun: _ContFn[Val, R]):
        self._fun = fun

    def bind(self, fun: _BindFn[Val, R, OtherVal]) -> Cont[R, OtherVal]:
        def bound(c: _C[OtherVal, R]) -> R:
            return self(lambda val: from_monad(fun(val))(c))

        return Cont(bound)

    @classmethod
    def unit(cls, value: OtherVal) -> Cont[R, OtherVal]:
        return Cont(lambda c: c(value))

    def __call__(self, c: _C[Val, R]) -> R:
        return self._fun(c)


def from_monad(monad: _Monad[R, Val]) -> Cont[R, Val]:
    if isinstance(monad, Cont):
        return monad
    raise TypeError("Monad is not Cont")
