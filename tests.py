from __future__ import annotations
import unittest
from typing import Tuple, Generic, TypeVar, Optional, List

from .currying import curry
from .monad import maybe, state, cont, do
from .monad.maybe import Just, Nothing, Maybe
from .monad.state import State
from .monad.cont import Cont


T = TypeVar("T")
U = TypeVar("U")


Stack = Tuple[T, ...]

IntStack = Stack[int]


class TestCurrying(unittest.TestCase):
    def test_sum(self) -> None:
        @curry
        def sum2(a: int, b: int) -> int:
            return a + b

        self.assertEqual(6, sum2(4)(2))

        @curry
        def sum5(a: int, b: int, c: int, d: int, e: int) -> int:
            return a + b + c + d + e

        self.assertEqual(17, sum5(5)(3)(1)(1)(7))

    def test_one(self) -> None:
        @curry
        def one() -> int:
            return 1

        self.assertEqual(1, one())

    def test_num(self) -> None:
        @curry
        def num(a: int) -> int:
            return a

        self.assertEqual(66, num(66))


class TestMaybe(unittest.TestCase):
    def test_seq1(self) -> None:
        # also tests associativity
        m = Just(5)
        res = (
            m.bind(lambda a: m.unit(a + 3))
            .bind(lambda b: m.unit(b * 11))
            .bind(lambda c: m.unit(c + 200))
        )
        self.assertEqual(288, maybe.value_from_monad(res))

    def test_seq2(self) -> None:
        # also tests associativity
        m = Just(5)
        res = m.bind(
            lambda a: m.unit(a + 3).bind(
                lambda b: m.unit(b * 11).bind(lambda c: m.unit((c + 200, a, b)))
            )
        )
        self.assertEqual((288, 5, 8), maybe.value_from_monad(res))

    def test_seq3(self) -> None:
        m = Just(5)
        res = ((m >= (lambda a: m.unit(a + 3))) >= (lambda b: m.unit(b * 11))) >= (
            lambda c: m.unit(c + 200)
        )
        self.assertEqual(288, maybe.value_from_monad(res))

    def test_seq4(self) -> None:
        m = Just(None)
        res = m >> Just(11) >= (lambda b: m.unit(b * 11))
        self.assertEqual(121, maybe.value_from_monad(res))

    def test_seq5(self) -> None:
        def foo(a: IntStack) -> Optional[IntStack]:
            return maybe.value_from_monad(
                Just(a + (1,)).bind(
                    lambda b: Just(b + (3,)).bind(
                        lambda c: Just.unit(c + (5,)).bind(lambda d: Just(d + b))
                    )
                )
            )

        self.assertEqual((1, 3, 5, 1), foo(()))

    def test_nothing1(self) -> None:
        m = Just(5)
        res = (
            m.bind(lambda a: Nothing())
            .bind(lambda b: m.unit(b * 11))
            .bind(lambda c: m.unit(c + 200))
        )
        self.assertIsInstance(res, Nothing)

    def test_nothing2(self) -> None:
        def foo(a: IntStack) -> Maybe[IntStack]:
            return maybe.from_monad(
                Just(a + (1,))
                >= (
                    lambda b: Nothing[IntStack]()
                    >= (lambda c: Just(c + (5,)) >= (lambda d: Just(d + b)))
                )
            )

        self.assertIsInstance(foo(()), Nothing)

    def test_do(self) -> None:
        def foo(a: IntStack) -> maybe.DoBlock[IntStack]:
            b = yield from Just(a + (1,))
            c = yield from Just(b + (3,))
            d = yield from Just(c + (5,))
            return Just(d + b)
        res = maybe.value_from_monad(do(foo(())))
        self.assertEqual((1, 3, 5, 1), res)


    def test_do_nothing(self) -> None:
        def foo(a: IntStack) -> maybe.DoBlock[IntStack]:
            b = yield from Just(a + (1,))
            c: IntStack = yield from Nothing()
            d = yield from Just(c + (5,))
            return Just(d + b)
        res = maybe.value_from_monad(do(foo(())))
        self.assertEqual(None, res)

    def xtest_wrong_type(self) -> None:
        # This method must trigger static type errors
        class Foo(Just[int]):
            pass

        m = Just(None)

        m.bind(lambda n: 5)
        m >> 10

        s: State[int, None] = State.unit(None)
        sm = s >> State.unit(None)
        m.bind(lambda n: sm)
        m >> sm

        (
            m.unit(1)
            .bind(lambda a: m.unit(a + 3))
            .bind(lambda b: m.unit([11]))
            .bind(lambda c: m.unit(c + 200))
        )


        def foo(a: int) -> maybe.DoBlock[int]:
            b = yield from Just(a + 3)
            c = yield from Just([11])
            return m.unit(b + c + 200)


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
    def test_seq1(self) -> None:
        m: StackS[str, None] = State.unit(None)
        ss = StackState[str]()
        seq = m.bind(
            lambda _: ss.pop.bind(
                lambda a: ss.push("a").bind(lambda b: ss.push("b") >> m.unit(a))
            )
        )
        res, stack = seq(("1", "2", "3"))
        self.assertEqual("3", res)
        self.assertEqual(("1", "2", "a", "b"), stack)

    def test_seq2(self) -> None:
        ss = StackState[str]()

        def seq(t: str) -> State[Stack[str], Tuple[str, str]]:
            return state.from_monad(
                (ss.pop >= (lambda _: ss.push("a")))
                >> ss.push(t)
                >> ss.push("b")
                >> ss.push("c")
                >> ss.pop
                >= (lambda a: ss.top >= (lambda b: State.unit((a, b))))
            )

        res, stack = seq("foo")(("1", "2", "3"))
        self.assertEqual(("c", "b"), res)
        self.assertEqual(("1", "2", "a", "foo", "b"), stack)

    def test_do(self) -> None:
        ss = StackState[str]()
        def seq(t: str) -> state.DoBlock[Stack[str], Tuple[str, str]]:
            yield ss.pop
            yield ss.push("a")
            yield ss.push(t)
            yield ss.push("b")
            yield ss.push("c")
            a = yield from ss.pop
            b = yield from ss.top
            return State.unit((a, b))

        res, stack = state.from_monad(do(seq("foo")))(("1", "2", "3"))
        self.assertEqual(("c", "b"), res)
        self.assertEqual(("1", "2", "a", "foo", "b"), stack)

    def xtest_wrong_type(self) -> None:
        # This method must trigger static type errors
        s1: State[Stack[int], None] = State.unit(None)
        sm1 = s1 >> State.unit(5)
        s2: State[Stack[str], None] = State.unit(None)
        sm2 = s2 >> State.unit(5)
        s1.bind(lambda n: s2)
        sm1 >= (lambda _: sm2)
        ss1 = StackState[int]()
        ss2 = StackState[str]()

        (
            s1.bind(
                lambda _: ss1.pop.bind(
                    lambda a: ss1.push(5).bind(lambda b: ss2.push("b") >> s1.unit(a))
                )
            )
        )

        (
            s1.bind(
                lambda _: ss1.pop.bind(
                    lambda a: ss1.push(5).bind(lambda b: ss1.push("b") >> s1.unit(a))
                )
            )
        )


        def seq() -> state.DoBlock[Stack[int], int]:
            a = yield from ss1.pop
            yield ss1.push(5)
            yield ss2.push("b")
            return s1.unit(a)


class TestCont(unittest.TestCase):
    def test_seq(self) -> None:
        def unit(val: T) -> Cont[T, T]:
            return Cont.unit(val)

        seq = Cont[List[int], List[int]](lambda c: c([1]) + c([80])).bind(
            lambda t1: unit(t1 + [2]).bind(
                lambda t2: unit(t2 + [7]).bind(lambda t3: unit(t3 + t2))
            )
        )
        exp = [1, 2, 7, 1, 2, 80, 2, 7, 80, 2]
        self.assertEqual(exp, seq(lambda val: val))

    def test_do(self) -> None:
        def unit(val: T) -> Cont[T, T]:
            return Cont.unit(val)

        def seq(d: int) -> cont.DoBlock[List[int], List[int]]:
            t1 = yield from Cont[List[int], List[int]](lambda c: c([1]))
            t2 = yield from unit(t1 + [2])
            t3 = yield from unit(t2 + [d])
            return unit(t3 + t2)

        exp = [1, 2, 77, 1, 2]
        self.assertEqual(exp, cont.from_monad(do(seq(77)))(lambda val: val))


if __name__ == "__main__":
    unittest.main()
