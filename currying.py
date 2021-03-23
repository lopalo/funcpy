from functools import wraps
from inspect import signature
from typing import TypeVar, Callable, Tuple, Any, overload

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")
E = TypeVar("E")
F = TypeVar("F")
Res = TypeVar("Res")

Fn0 = Callable[[], Res]
Fn1 = Callable[[A], Res]
Fn2 = Callable[[A, B], Res]
Fn3 = Callable[[A, B, C], Res]
Fn4 = Callable[[A, B, C, D], Res]
Fn5 = Callable[[A, B, C, D, E], Res]
Fn6 = Callable[[A, B, C, D, E, F], Res]


@overload
def curry(fun: Fn0[Res]) -> Fn0[Res]:
    ...


@overload
def curry(fun: Fn1[A, Res]) -> Fn1[A, Res]:
    ...


@overload
def curry(fun: Fn2[A, B, Res]) -> Fn1[A, Fn1[B, Res]]:
    ...


@overload
def curry(fun: Fn3[A, B, C, Res]) -> Fn1[A, Fn1[B, Fn1[C, Res]]]:
    ...


@overload
def curry(fun: Fn4[A, B, C, D, Res]) -> Fn1[A, Fn1[B, Fn1[C, Fn1[D, Res]]]]:
    ...


@overload
def curry(fun: Fn5[A, B, C, D, E, Res]) -> Fn1[A, Fn1[B, Fn1[C, Fn1[D, Fn1[D, Res]]]]]:
    ...


def curry(fun: Callable[..., Any]) -> Any:
    arg_count = len(signature(fun).parameters)

    def _curry(_fun: Callable[..., Any], _args: Tuple[Any, ...]) -> Callable[..., Any]:
        @wraps(_fun)
        def _next(*args: Any) -> Any:
            new_args = _args + args
            if len(new_args) >= arg_count:
                return fun(*new_args)
            return _curry(_next, new_args)

        return _next

    @wraps(fun)
    def curried(*args: Any) -> Any:
        return _curry(curried, ())(*args)

    return curried
