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

    def bind(self, fun):
        if not callable(fun):
            raise TypeError("{} is not callable".format(fun))
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
    """ Not quite correct implementation of the "do" notation """

    if not isgeneratorfunction(fun):
        raise ValueError("Function {} must return a generator".format(fun))

    @wraps(fun)
    def _do(*args, **kwargs):
        def _next(val):
            nonlocal cont
            cont = True
            try:
                return gen.send(val)
            except StopIteration as e:
                cont = False
                return e.value

        cont = True # need for the monad that may interrupt a computation
        gen = fun(*args, **kwargs)
        val = next(gen)
        if not isinstance(val, Monad):
            error = "Wrong type of {}. Must be an instance of Monad"
            raise TypeError(error.format(val))
        while cont:
            cont = False
            val = val.bind(_next)
        return val
    return _do


