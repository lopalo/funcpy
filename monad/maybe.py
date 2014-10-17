from monad import Monad


class Maybe(Monad):

    def bind_implementation(self, fun):
        if isinstance(self, Nothing):
            return Nothing()
        else:
            return fun(self._value)

    @staticmethod
    def constructors():
        return (Nothing, Just)

    @classmethod
    def ret(cls, value):
        return Just(value)


class Nothing(Maybe):

    def __init__(self): pass


class Just(Maybe):

    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value
