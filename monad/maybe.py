from __future__ import annotations
import typing as t
from . import Monad as BaseMonad, Val, OtherVal


@t.final
class _Maybe:
    "Type tag that makes 'Maybe' monad compatible only with itself"
    pass


_Monad = BaseMonad[_Maybe, Val]
_BindFn = t.Callable[[Val], BaseMonad[_Maybe, OtherVal]]


class _Unit:
    @staticmethod
    def unit(value: OtherVal) -> Just[OtherVal]:
        return Just(value)


@t.final
class Just(_Unit, _Monad[Val]):
    def __init__(self, value: Val) -> None:
        self._value = value

    def bind(self, fun: _BindFn[Val, OtherVal]) -> _Monad[OtherVal]:
        return fun(self._value)

    @property
    def value(self) -> Val:
        return self._value


@t.final
class Nothing(_Unit, _Monad[Val]):
    def __init__(self) -> None:
        pass

    def bind(self, _: _BindFn[Val, OtherVal]) -> _Monad[OtherVal]:
        return Nothing()


Maybe = t.Union[Just[Val], Nothing[Val]]

DoBlock = t.Generator[_Monad[t.Any], None, _Monad[Val]]


def from_monad(monad: _Monad[Val]) -> Maybe[Val]:
    if isinstance(monad, Just):
        return monad
    if isinstance(monad, Nothing):
        return monad
    raise TypeError("Monad is neither Just nor Nothing")


def value(maybe: Maybe[Val], default: t.Optional[Val] = None) -> t.Optional[Val]:
    if isinstance(maybe, Just):
        return maybe.value
    return default


def value_from_monad(
    monad: _Monad[Val], default: t.Optional[Val] = None
) -> t.Optional[Val]:
    return value(from_monad(monad), default)
