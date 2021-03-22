from . import Monad

class Cont(Monad):

    """
    Do not use "do" notation if continuation is called more than once,
    because a generator cannot be rewound back.
    """

    def __init__(self, fun=lambda c: c()):
        self._check_callable(fun)
        self._fun = fun

    def bind_implementation(self, fun):
        def bound(c):
            return self(lambda val: self._check_type(fun(val))(c))
        return Cont(bound)

    @staticmethod
    def constructors():
        return (Cont,)

    @classmethod
    def ret(cls, value):
        return Cont(lambda c: c(value))

    def __call__(self, c):
        return self._fun(c)


def call_cc(fun):
    return Cont(lambda h: fun(lambda a: Cont(lambda _: h(a)))(h))

