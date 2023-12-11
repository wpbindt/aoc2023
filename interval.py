from __future__ import annotations

import random
from dataclasses import dataclass
from functools import wraps
from typing import TypeVar, Callable


@dataclass(frozen=True)
class Interval:
    start: int
    end: int  # inclusive

    def combine(self, other: Interval) -> Interval:
        return Interval(min(self.start, other.start), max(self.end, other.end))

    def disjoint(self, other: Interval) -> bool:
        return self.end < other.start or other.end < self.start

    def __le__(self, other: Interval) -> bool:
        return other.start <= self.start and self.end <= other.end

    def to_list(self) -> list[int]:
        return list(range(self.start, self.end + 1))

    def intersect(self, other: Interval) -> set[Interval]:
        if self.disjoint(other):
            return set()
        return {Interval(
            start=max(self.start, other.start),
            end=min(self.end, other.end),
        )}

    def complement(self, other: Interval) -> set[Interval]:
        if self.disjoint(other):
            return {self}
        if self <= other:
            return set()
        if other.start <= self.start:
            return {Interval(other.end + 1, self.end)}
        if other.end >= self.end:
            return {Interval(self.start, other.start - 1)}
        return {
            Interval(self.start, other.start - 1),
            Interval(other.end + 1, self.end)
        }


def explode(interval: Interval, intervals_to_explode_by: set[Interval]) -> set[Interval]:
    if len(intervals_to_explode_by) == 0:
        return {interval}

    interval_to_explode_by, *remainder = intervals_to_explode_by
    first_explosion = {
        *interval.intersect(interval_to_explode_by),
        *interval.complement(interval_to_explode_by),
    }
    return set.union(*[
        explode(shrapnel, remainder)
        for shrapnel in first_explosion
    ])


def clean_up(intervals: set[Interval]) -> set[Interval]:
    result = []
    for interval in intervals:
        for ix, other_interval in enumerate(result):
            if not interval.disjoint(other_interval):
                result[ix] = interval.combine(other_interval)
                break
        else:
            result.append(interval)

    result_set = set(result)
    for interval in result_set:
        for other_interval in result_set:
            if interval != other_interval and not interval.disjoint(other_interval):
                return clean_up(result_set)

    return set(result)


assert Interval(2, 5).to_list() == [2, 3, 4, 5]
assert Interval(2, 9) <= Interval(1, 100)
assert not (Interval(2, 9) <= Interval(3, 100))
assert not (Interval(2, 9) <= Interval(1, 5))
assert Interval(2, 9).disjoint(Interval(10, 100))
assert Interval(2, 9).intersect(Interval(10, 100)) == set()
assert Interval(2, 9).intersect(Interval(2, 9)) == {Interval(2, 9)}
assert Interval(2, 9).intersect(Interval(1, 9)) == {Interval(2, 9)}
assert Interval(2, 9).intersect(Interval(2, 7)) == {Interval(2, 7)}
assert Interval(2, 9).intersect(Interval(3, 9)) == {Interval(3, 9)}
assert Interval(2, 9).complement(Interval(2, 9)) == set()
assert Interval(2, 9).complement(Interval(3, 9)) == {Interval(2, 2)}
assert Interval(2, 9).complement(Interval(2, 8)) == {Interval(9, 9)}
assert Interval(2, 9).complement(Interval(3, 8)) == {Interval(2, 2), Interval(9, 9)}
assert Interval(2, 9).complement(Interval(300, 400)) == {Interval(2, 9)}
assert not Interval(2, 9).disjoint(Interval(2, 100))
assert Interval(2, 9).disjoint(Interval(-3, -1))
assert Interval(2, 5).combine(Interval(4, 9)) == Interval(2, 9)

assert explode(Interval(2, 9), set()) == {Interval(2, 9)}
assert explode(Interval(2, 9), {Interval(2, 9)}) == {Interval(2, 9)}
assert explode(Interval(2, 9), {Interval(2, 3)}) == {Interval(2, 3), Interval(4, 9)}
assert explode(Interval(2, 9), {Interval(4, 5)}) == {Interval(2, 3), Interval(4, 5), Interval(6, 9)}
assert explode(Interval(2, 9), {Interval(40, 50)}) == {Interval(2, 9)}
assert explode(Interval(2, 9), {Interval(4, 5), Interval(6, 7)}) == {Interval(2, 3), Interval(4, 5), Interval(6, 7), Interval(8, 9)}

assert clean_up(set()) == set()
assert clean_up({Interval(9, 9)}) == {Interval(9, 9)}
assert clean_up({Interval(9, 9), Interval(2, 9)}) == {Interval(2, 9)}, clean_up({Interval(9, 9), Interval(2, 9)})
assert clean_up({Interval(1, 9), Interval(2, 4), Interval(3, 5)}) == {Interval(1, 9)}


def generate_random_interval(lower: int = -1000, higher: int = 500) -> Interval:
    start = random.randint(lower, higher)
    end = random.randint(start, higher)
    return Interval(start, end)


T = TypeVar('T')


def generate_disjoint_set() -> set[Interval]:
    set_size = random.randint(0, 20)
    result = set()
    lower = -1000
    for _ in range(set_size):
        generated_interval = generate_random_interval(lower=lower)
        result.add(generated_interval)
        lower = generated_interval.end
    return result


def generate_set_of_intervals() -> set[Interval]:
    return {
        generate_random_interval()
        for _ in range(random.randint(0, 40))
    }


def generate_explosion_test_data() -> tuple[Interval, set[Interval]]:
    return generate_random_interval(), generate_disjoint_set()


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


@hypothesis(generate_explosion_test_data)
def shrapnel_should_be_disjoint_or_contained(
    test_data: tuple[Interval, set[Interval]],
) -> None:
    interval, intervals_to_explode_by = test_data
    exploded = explode(interval, intervals_to_explode_by)
    for shrapnel in exploded:
        for exploder in intervals_to_explode_by:
            assert shrapnel.disjoint(exploder) or shrapnel <= exploder, f'expected {exploder} to contain or be disjoint from {shrapnel}'


@hypothesis(generate_explosion_test_data)
def shrapnel_should_add_back_up_to_original(
    test_data: tuple[Interval, set[Interval]],
) -> None:
    interval, intervals_to_explode_by = test_data
    explosion = explode(interval, intervals_to_explode_by)
    shrapnel_list = [
        integer
        for shrapnel in explosion
        for integer in shrapnel.to_list()
    ]
    assert interval.to_list() == sorted(shrapnel_list), f'expected {interval.to_list()} got {sorted(shrapnel_list)}'


@hypothesis(generate_set_of_intervals)
def clean_up_should_preserve_contents(test_data: set[Interval]) -> None:
    cleaned_up = clean_up(intervals=test_data)
    actual = [
        element
        for interval in cleaned_up
        for element in interval.to_list()
    ]
    expected = [
        element
        for interval in test_data
        for element in interval.to_list()
    ]
    assert set(actual) == set(expected), f'expected {set(expected)}, got {set(actual)}'


@hypothesis(generate_set_of_intervals)
def clean_up_shrinks(test_data: set[Interval]) -> None:
    cleaned_up = clean_up(test_data)
    assert len(cleaned_up) <= len(test_data)


for hypo in hypotheses:
    hypo()
