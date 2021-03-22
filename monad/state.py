from __future__ import annotations
import typing as t
from . import Monad as BaseMonad, Val, OtherVal


S = t.TypeVar("S")


@t.final
class _State(t.Generic[S]):
    "Type tag that makes 'State' monad and its content compatible only with themselves"
    pass


_Monad = BaseMonad[_State[S], Val]
_BindFn = t.Callable[[Val], BaseMonad[_State[S], OtherVal]]
_StateFn = t.Callable[[S], t.Tuple[Val, S]]


@t.final
class State(_Monad[S, Val]):
    def __init__(self, fun: _StateFn[S, Val]):
        self._fun = fun

    def bind(self, fun: _BindFn[Val, S, OtherVal]) -> State[S, OtherVal]:
        def bound(s: S) -> t.Tuple[OtherVal, S]:
            (x, new_s) = self(s)
            sm = fun(x)
            return from_monad(sm)(new_s)

        return State(bound)

    @staticmethod
    def unit(value: OtherVal) -> State[S, OtherVal]:
        return State(lambda s: (value, s))

    def __call__(self, state: S) -> t.Tuple[Val, S]:
        return self._fun(state)


def from_monad(monad: _Monad[S, Val]) -> State[S, Val]:
    if isinstance(monad, State):
        return monad
    raise TypeError("Monad is not State")
