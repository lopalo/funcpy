from functools import wraps
from inspect import isgeneratorfunction

class Monad(object):

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        cls._check_type(obj)
        return obj

    @classmethod
    def _check_type(cls, obj):
        constructors = cls.constructors()
        for tp in constructors:
            if type(obj) is tp:
                break
        else:
            error = "Wrong type of {}. Must be one of {}"
            raise TypeError(error.format(obj, constructors))
        return obj

    @staticmethod
    def _check_callable(fun):
        if not callable(fun):
            raise TypeError("{} is not callable".format(fun))
        return fun

    def bind(self, fun):
        self._check_callable(fun)
        res = self.bind_implementation(fun)
        self._check_type(res)
        return res

    __ge__ = bind

    def __rshift__(self, obj):
        self._check_type(obj)
        return self.bind(lambda _: obj)

    def bind_implementation(self, fun):
        raise NotImplementedError

    @staticmethod
    def constructors():
        raise NotImplementedError

    @classmethod
    def ret(cls, value):
        raise NotImplementedError

    #TODO: maybe add fail


def do(monad_cls):
    """ Limited implementation of the "do" notation """

    if not issubclass(monad_cls, Monad):
        error = "Wrong type of {}. Must be an instance of Monad"
        raise TypeError(error.format(monad_cls))

    def wrapper(fun):

        if not isgeneratorfunction(fun):
            raise ValueError("Function {} must return a generator".format(fun))

        @wraps(fun)
        def _do(*args, **kwargs):
            def _next(val):
                try:
                    next_val = gen.send(val)
                    monad_cls._check_type(next_val)
                    return next_val.bind(_next)
                except StopIteration as e:
                    return monad_cls._check_type(e.value)

            gen = fun(*args, **kwargs)
            val = next(gen)
            monad_cls._check_type(val)
            return val.bind(_next)
        return _do
    return wrapper


