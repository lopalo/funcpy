from monad import Monad


class State(Monad):

    def __init__(self, fun=lambda s: (None, s)):
        self._check_callable(fun)
        self._fun = fun

    def bind_implementation(self, fun):
        def bound(s):
            (x, new_s) = self(s)
            st = fun(x)
            self._check_type(st)
            return st(new_s)
        return State(bound)

    @staticmethod
    def constructors():
        return (State,)

    @classmethod
    def ret(cls, value):
        return State(lambda s: (value, s))

    def __call__(self, state):
        return self._fun(state)

