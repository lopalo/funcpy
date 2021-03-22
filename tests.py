from __future__ import annotations
import unittest
from typing import Optional, Tuple, List, Generic, TypeVar

# from .currying import curry
# from .monad import do
from .monad.maybe import Just, Nothing, value_from_monad
from .monad.state import State
from .monad.cont import Cont, call_cc


# class TestCurrying(unittest.TestCase):
#
#     def test_sum(self):
#         @curry
#         def sum2(a, b):
#             return a + b
#         self.assertEqual(6, sum2(4)(2))
#
#         @curry
#         def sum5(a, b, c, d, e):
#             return a + b + c + d + e
#
#         self.assertEqual(17, sum5(5)(3)(1)(1)(7))
#         self.assertEqual(17, sum5(5, 3)(1)(1)(7))
#         self.assertEqual(17, sum5(5)(3, 1, 1)(7))
#         self.assertEqual(17, sum5(5)(3)(1, 1, 7))
#
#     def test_fun_dict(self):
#         @curry
#         def sum5(a, b, c, d, e):
#             return a + b + c + d + e
#
#         sum5.a = 11
#         foo = sum5(44)(8)
#         foo.b = 22
#         bar = foo(32)(0)
#         self.assertEqual("sum5", bar.__name__)
#         self.assertEqual(11, bar.a)
#         self.assertEqual(22, bar.b)
#         self.assertIsNone(getattr(sum5, 'b', None))
#
#     def test_one(self):
#         @curry
#         def one():
#             return 1
#         self.assertEqual(1, one())
#
#     def test_num(self):
#         @curry
#         def num(a):
#             return a
#         self.assertEqual(66, num(66))
#
#     def test_excess_args(self):
#         @curry
#         def fun(a, b): pass
#         with self.assertRaises(TypeError):
#             fun(1, 2, 4)


class TestMaybe(unittest.TestCase):
    def test_seq1(self) -> None:
        # also tests associativity
        m = Just(5)
        res = (
            m.bind(lambda a: m.unit(a + 3))
            .bind(lambda b: m.unit(b * 11))
            .bind(lambda c: m.unit(c + 200))
        )
        self.assertEqual(288, value_from_monad(res))

    def test_seq2(self) -> None:
        # also tests associativity
        m = Just(5)
        res = m.bind(
            lambda a: m.unit(a + 3).bind(
                lambda b: m.unit(b * 11).bind(lambda c: m.unit((c + 200, a, b)))
            )
        )
        self.assertEqual((288, 5, 8), value_from_monad(res))

    def test_seq3(self) -> None:
        m = Just(5)
        res = ((m >= (lambda a: m.unit(a + 3))) >= (lambda b: m.unit(b * 11))) >= (
            lambda c: m.unit(c + 200)
        )
        self.assertEqual(288, value_from_monad(res))

    def test_seq4(self) -> None:
        m = Just(5)
        res = m >> Just(11) >= (lambda b: m.unit(b * 11))
        self.assertEqual(121, value_from_monad(res))

    def test_nothing(self) -> None:
        m = Just(5)
        res = (
            m.bind(lambda a: Nothing())
            .bind(lambda b: m.unit(b * 11))
            .bind(lambda c: m.unit(c + 200))
        )
        self.assertIsInstance(res, Nothing)

    def xtest_wrong_type(self) -> None:
        # This method must trigger static type errors
        class Foo(Just[int]):
            pass

        m = Just(1)

        m.bind(lambda n: 5)
        m >> 10

        s: State[int, int] = State.unit(3)
        sm = s >> State.unit(5)
        m.bind(lambda n: sm)
        m >> sm

        (
            m.bind(lambda a: m.unit(a + 3))
            .bind(lambda b: m.unit([11]))
            .bind(lambda c: m.unit(c + 200))
        )

    #
    # def test_do(self):
    #     @do(_Maybe)
    #     def foo(a):
    #         b = yield Just(a + (1,))
    #         c = yield Just(b + (3,))
    #         d = yield _Maybe.ret(c + (5,))
    #         return Just(d + b)
    #     self.assertEqual((1, 3, 5, 1), foo(()).value)
    #
    # def test_do_nothing(self):
    #     @do(_Maybe)
    #     def foo(a):
    #         b = yield Just(a + (1,))
    #         c = yield Nothing()
    #         d = yield _Maybe.ret(c + (5,))
    #         return Just(d + b)
    #     self.assertIsInstance(foo(()), Nothing)
    #
    # def test_do_wrong_type(self):
    #     @do(_Maybe)
    #     def foo(a):
    #         yield Just(5)
    #         yield 4
    #     with self.assertRaises(TypeError):
    #         foo(10)
    #     @do(_Maybe)
    #     def bar(a):
    #         yield 5
    #         yield Just(4)
    #     with self.assertRaises(TypeError):
    #         bar(10)
    #     @do(_Maybe)
    #     def baz(a):
    #         yield Just(3)
    #         return 5
    #     with self.assertRaises(TypeError):
    #         baz(10)


T = TypeVar("T")
U = TypeVar("U")


Stack = Tuple[T, ...]


StackS = State[Stack[T], U]


class StackState(Generic[T]):
    @staticmethod
    def push(value: T) -> StackS[T, None]:
        return State(lambda stack: (None, stack + (value,)))

    @property
    def pop(_) -> StackS[T, T]:
        return State(lambda stack: (stack[-1], stack[:-1]))

    @property
    def top(_) -> StackS[T, T]:
        return State(lambda stack: (stack[-1], stack))


class TestState(unittest.TestCase):
    def test_seq(self) -> None:
        m: StackS[str, None] = State.unit(None)
        ss = StackState[str]()
        seq = m.bind(
            lambda _: ss.pop.bind(
                lambda a: ss.push("a").bind(lambda b: ss.push("b") >> m.unit(a))
            )
        )
        res, stack = seq(("1", "2", "3"))
        self.assertEqual(3, res)
        self.assertEqual((1, 2, "a", "b"), stack)

    def xtest_wrong_type(self) -> None:
        # This method must trigger static type errors
        s1: State[Stack[int], int] = State.unit(3)
        sm1 = s1 >> State.unit(5)
        s2: State[Stack[str], int] = State.unit(3)
        sm2 = s2 >> State.unit(5)
        s1.bind(lambda n: s2)
        sm1 >> sm2
        ss1 = StackState[int]()
        ss2 = StackState[str]()

        (
            s1.bind(
                lambda _: ss1.pop.bind(
                    lambda a: ss1.push(5).bind(lambda b: ss2.push("b") >> s1.unit(a))
                )
            )
        )

    # def test_do(self):
    #     @do(State)
    #     def seq(t):
    #         yield pop
    #         yield push("a")
    #         yield push(t)
    #         yield push("b")
    #         yield push("c")
    #         a = yield pop
    #         b = yield top
    #         return State.ret((a, b))
    #
    #     res, stack = seq("foo")(Stack(1, 2, 3))
    #     self.assertEqual(("c", "b"), res)
    #     self.assertEqual((1, 2, "a", "foo", "b"), stack.tuple)


# class TestCont(unittest.TestCase):
#
#     def test_seq(self):
#         seq = (Cont(lambda c: c((1,)) + c((80,)))
#                .bind(lambda t1: Cont.ret(t1 + (2,))
#                .bind(lambda t2: Cont.ret(t2 + (7,))
#                .bind(lambda t3: Cont.ret(t3 + t2)))))
#         exp = (1, 2, 7, 1, 2, 80, 2, 7, 80, 2)
#         self.assertEqual(exp, seq(lambda val: val))
#
#     def test_do(self):
#         @do(Cont)
#         def seq(d):
#             t1 = yield Cont(lambda c: c((1,)))
#             t2 = yield Cont.ret(t1 + (2,))
#             t3 = yield Cont.ret(t2 + (d,))
#             return Cont.ret(t3 + t2)
#         exp = (1, 2, 77, 1, 2)
#         self.assertEqual(exp, seq(77)(lambda val: val))
#
#     def test_wrong_do(self):
#         @do(Cont)
#         def seq(d):
#             t1 = yield Cont(lambda c: c((1,)) + c((80,)))
#             t2 = yield Cont.ret(t1 + (2,))
#             t3 = yield Cont.ret(t2 + (d,))
#             return Cont.ret(t3 + t2)
#         with self.assertRaises(TypeError):
#             seq(77)(lambda val: val)
#
#     def test_call_cc(self):
#         @do(Cont)
#         def seq(call):
#             @do(Cont)
#             def sub_seq(c):
#                 if call:
#                     yield c(100)
#                 t2 = yield Cont.ret(11)
#                 return Cont.ret(t2 + 200)
#             t1 = yield call_cc(sub_seq)
#             return Cont.ret(t1 + 12)
#         self.assertEqual(112, seq(True)(lambda v: v))
#         self.assertEqual(223, seq(False)(lambda v: v))


if __name__ == "__main__":
    unittest.main()
