from __future__ import annotations

import random
from fractions import Fraction
from functools import lru_cache
from typing import TypeVar

from parsing import separated_by, integer
from property_based_testing.api import inject

T = TypeVar('T')

example_data = """0 3 6 9 12 15\n1 3 6 10 15 21\n10 13 16 21 30 45"""


@lru_cache(maxsize=None)
def frac_binom(n: int, k: int) -> Fraction:
    if k == 0 or n == k:
        return Fraction(1, 1)
    return frac_binom(n - 1, k - 1) * Fraction(n, k)


def binom(n: int, k: int) -> int:
    return int(frac_binom(n, k))


def generate_nonnegative_integer() -> int:
    return random.randint(0, 200)


def generate_positive_binomial_argument() -> tuple[int, int]:
    n = random.randint(2, 200)
    k = random.randint(1, n - 1)
    return n, k


@inject(generate_nonnegative_integer)
def property_test_binomial_with_0_bottom_is_1(n: int) -> None:
    assert binom(n, 0) == 1


@inject(generate_nonnegative_integer)
def property_test_binomial_with_n_bottom_is_1(n: int) -> None:
    assert binom(n, n) == 1


@inject(generate_positive_binomial_argument)
def property_test_pascal_identity(nk: tuple[int, int]) -> None:
    n, k = nk
    assert binom(n, k) == binom(n - 1, k - 1) + binom(n - 1, k)


def extrapolate(row: list[int]) -> int:
    summands = [
        ((-1) ** i) * sum(
            ((-1) ** (j)) * binom(i, j) * row[i - j]
            for j in range(i + 1)
        )
        for i in range(len(row))
    ]
    return sum(summands)


def main_parsed(rows: list[list[int]]) -> int:
    return sum(
        extrapolate(row)
        for row in rows
    )


integers = separated_by(integer, ' ')


def main(to_parse: str) -> int:
    lines = to_parse.split('\n')
    parsed = [
        integers(line).result
        for line in lines
    ]
    result = main_parsed(parsed)
    print(result)
    return result

assert main(example_data) == 2

with open('day9_input') as f:
    to_parse = f.read()

print(main(to_parse))
