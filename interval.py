from __future__ import annotations
from dataclasses import dataclass
import random
from typing import TypeVar, Callable


@dataclass(frozen=True)
class Interval:
    start: int
    end: int  # inclusive

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
assert explode(Interval(2, 9), set()) == {Interval(2, 9)}
assert explode(Interval(2, 9), {Interval(2, 9)}) == {Interval(2, 9)}
assert explode(Interval(2, 9), {Interval(2, 3)}) == {Interval(2, 3), Interval(4, 9)}
assert explode(Interval(2, 9), {Interval(4, 5)}) == {Interval(2, 3), Interval(4, 5), Interval(6, 9)}
assert explode(Interval(2, 9), {Interval(40, 50)}) == {Interval(2, 9)}
assert explode(Interval(2, 9), {Interval(4, 5), Interval(6, 7)}) == {Interval(2, 3), Interval(4, 5), Interval(6, 7), Interval(8, 9)}


def shrapnel_should_be_disjoint_or_contained(interval: Interval, intervals_to_explode_by: set[Interval]) -> None:
    exploded = explode(interval, intervals_to_explode_by)
    for shrapnel in exploded:
        for exploder in intervals_to_explode_by:
            assert shrapnel.disjoint(exploder) or shrapnel <= exploder, f'expected {exploder} to contain or be disjoint from {shrapnel}'


def shrapnel_should_add_back_up_to_original(interval: Interval, intervals_to_explode_by: set[Interval]) -> None:
    explosion = explode(interval, intervals_to_explode_by)
    shrapnel_list = [
        integer
        for shrapnel in explosion
        for integer in shrapnel.to_list()
    ]
    assert interval.to_list() == sorted(shrapnel_list), f'expected {interval.to_list()} got {sorted(shrapnel_list)}'


def plurality(interval: Interval, intervals_to_explode_by: set[Interval]) -> None:
    explosion = explode(interval, intervals_to_explode_by)
    running_explosion = {interval}
    for explody_interval in intervals_to_explode_by:
        new_running_explosion = set()
        for shrapnel in running_explosion:
            new_running_explosion |= explode(shrapnel, {explody_interval})
        running_explosion = new_running_explosion

    assert explosion == running_explosion


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

test_data = ((generate_random_interval(), generate_disjoint_set()) for _ in range(20000))

for index, test_datum in enumerate(test_data):
    interval, intervals_to_explode_by = test_datum
    if index % 1000 == 0:
        print(f'{index} test cases done')
    shrapnel_should_add_back_up_to_original(interval, intervals_to_explode_by)
    shrapnel_should_be_disjoint_or_contained(interval, intervals_to_explode_by)
