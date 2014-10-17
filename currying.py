from functools import wraps
from inspect import getargspec


def curry(fun):
    def _curry(_fun, _args):
        @wraps(_fun)
        def _next(*args):
            new_args = _args + args
            if len(new_args) >= arg_count:
                return fun(*new_args)
            return _curry(_next, new_args)
        return _next

    @wraps(fun)
    def curried(*args):
        return _curry(curried, ())(*args)

    arg_count = len(getargspec(fun).args)
    return curried




