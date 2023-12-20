from __future__ import annotations

import random
from fractions import Fraction
from functools import wraps, lru_cache
from typing import Callable, TypeVar

T = TypeVar('T')


@lru_cache(maxsize=None)
def frac_binom(n: int, k: int) -> Fraction:
    if k == 0 or n == k:
        return Fraction(1, 1)
    return frac_binom(n - 1, k - 1) * Fraction(n, k)


def binom(n: int, k: int) -> int:
    return int(frac_binom(n, k))


hypotheses = set()


def hypothesis(
        argument_generator: Callable[[], T],
        iterations: int = 10000,
) -> Callable[[Callable[[T], None]], Callable[[T], None]]:
    def decorator(f: Callable[[T], None]) -> Callable[[], None]:
        @wraps(f)
        def wrapped() -> None:
            print(f'testing {f.__name__}')
            test_data = (argument_generator() for _ in range(iterations))
            for ix, datum in enumerate(test_data):
                if ix % 1000 == 0:
                    print(f'iteration {ix} out of {iterations}')
                f(datum)
        hypotheses.add(wrapped)
        return f
    return decorator


def generate_nonnegative_integer() -> int:
    return random.randint(0, 200)


def generate_positive_binomial_argument() -> tuple[int, int]:
    n = random.randint(2, 200)
    k = random.randint(1, n - 1)
    return n, k


@hypothesis(generate_nonnegative_integer)
def binomial_with_0_bottom_is_1(n: int) -> None:
    assert binom(n, 0) == 1


@hypothesis(generate_nonnegative_integer)
def binomial_with_n_bottom_is_1(n: int) -> None:
    assert binom(n, n) == 1


@hypothesis(generate_positive_binomial_argument)
def pascal_identity(nk: tuple[int, int]) -> None:
    n, k = nk
    assert binom(n, k) == binom(n - 1, k - 1) + binom(n - 1, k)


def extrapolate(row: list[int]) -> int:
    reversed_row = list(reversed(row))
    return sum(
        sum(
            ((-1) ** j) * binom(i, j) * reversed_row[j]
            for j in range(i + 1)
        )
        for i in range(len(row) + 1)
    )


def main(rows: list[list[int]]) -> int:
    return sum(
        extrapolate(row)
        for row in rows
    )


if __name__ == '__main__':
    for hypo in hypotheses:
        hypo()
