import unittest

from currying import curry
from monad import do
from monad.maybe import Maybe, Just, Nothing


class TestCurrying(unittest.TestCase):

    def test_sum(self):
        @curry
        def sum2(a, b):
            return a + b
        self.assertEqual(6, sum2(4)(2))

        @curry
        def sum5(a, b, c, d, e):
            return a + b + c + d + e

        self.assertEqual(17, sum5(5)(3)(1)(1)(7))
        self.assertEqual(17, sum5(5, 3)(1)(1)(7))
        self.assertEqual(17, sum5(5)(3, 1, 1)(7))
        self.assertEqual(17, sum5(5)(3)(1, 1, 7))

    def test_fun_dict(self):
        @curry
        def sum5(a, b, c, d, e):
            return a + b + c + d + e

        sum5.a = 11
        foo = sum5(44)(8)
        foo.b = 22
        bar = foo(32)(0)
        self.assertEqual("sum5", bar.__name__)
        self.assertEqual(11, bar.a)
        self.assertEqual(22, bar.b)
        self.assertIsNone(getattr(sum5, 'b', None))

    def test_one(self):
        @curry
        def one():
            return 1
        self.assertEqual(1, one())

    def test_num(self):
        @curry
        def num(a):
            return a
        self.assertEqual(66, num(66))

    def test_excess_args(self):
        @curry
        def fun(a, b): pass
        with self.assertRaises(TypeError):
            fun(1, 2, 4)



class TestMaybe(unittest.TestCase):

    def test_seq1(self):
        # also tests associativity
        res = (Just(5)
               .bind(lambda a: Maybe.ret(a + 3))
               .bind(lambda b: Maybe.ret(b * 11))
               .bind(lambda c: Maybe.ret(c + 200)))
        self.assertEqual(288, res.value)

    def test_seq2(self):
        # also tests associativity
        res = (Just(5)
               .bind(lambda a: Maybe.ret(a + 3)
               .bind(lambda b: Maybe.ret(b * 11)
               .bind(lambda c: Maybe.ret((c + 200, a, b))))))
        self.assertEqual((288, 5, 8), res.value)

    def test_seq3(self):
        res = (((Just(5)
               >= (lambda a: Maybe.ret(a + 3)))
               >= (lambda b: Maybe.ret(b * 11)))
               >= (lambda c: Maybe.ret(c + 200)))
        self.assertEqual(288, res.value)

    def test_seq4(self):
        res = (Just(5)
               >> Just(11)
               >= (lambda b: Maybe.ret(b * 11)))
        self.assertEqual(121, res.value)

    def test_nothing(self):
        res = (Just(5)
               .bind(lambda a: Nothing())
               .bind(lambda b: Maybe.ret(b * 11))
               .bind(lambda c: Maybe.ret(c + 200)))
        self.assertIsInstance(res, Nothing)

    def test_wrong_type(self):
        class Foo(Just): pass
        with self.assertRaises(TypeError):
            Foo()
        with self.assertRaises(TypeError):
            Just(1).bind(lambda n: 5)
        with self.assertRaises(TypeError):
            Just(2) >> 10
        with self.assertRaises(TypeError):
            Just(2) >= 10

    def test_do(self):
        @do
        def foo(a):
            b = yield Just(a + (1,))
            c = yield Just(b + (3,))
            d = yield Maybe.ret(c + (5,))
            return Just(d + b)
        self.assertEqual((1, 3, 5, 1), foo(()).value)

    def test_do_nothing(self):
        @do
        def foo(a):
            b = yield Just(a + (1,))
            c = yield Nothing()
            d = yield Maybe.ret(c + (5,))
            return Just(d + b)
        self.assertIsInstance(foo(()), Nothing)

    def test_do_wrong_type(self):
        @do
        def foo(a):
            yield Just(5)
            yield 4
        with self.assertRaises(TypeError):
            foo(10)
        @do
        def bar(a):
            yield 5
            yield Just(4)
        with self.assertRaises(TypeError):
            bar(10)
        @do
        def baz(a):
            yield Just(3)
            return 5
        with self.assertRaises(TypeError):
            baz(10)



if __name__ == '__main__':
    unittest.main()
