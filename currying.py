from functools import wraps
from inspect import signature


#TODO: use typing.overload for different arities
def curry(fun):
    arg_count = len(signature(fun).parameters)
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

    return curried




