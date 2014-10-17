from functools import wraps
from inspect import isgeneratorfunction

class Monad(object):

    def __new__(cls, *args, **kwargs):
        obj = super(Monad, cls).__new__(cls, *args, **kwargs)
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
            raise ValueError(error.format(obj, constructors))

    def bind(self, fun):
        assert callable(fun), fun
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


def do(fun):
    if not isgeneratorfunction(fun):
        raise ValueError("Function '{}' must return a generator",format(fun))
    @wraps(fun)
    def _do(*args, **kwargs):
        #TODO
        pass
    return _do


