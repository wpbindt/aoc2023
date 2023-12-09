from __future__ import annotations

from functools import cached_property

from parsing import *
from dataclasses import dataclass

example_data = """seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48

soil-to-fertilizer map:
0 15 37
37 52 2
39 0 15

fertilizer-to-water map:
49 53 8
0 11 42
42 0 7
57 7 4

water-to-light map:
88 18 7
18 25 70

light-to-temperature map:
45 77 23
81 45 19
68 64 13

temperature-to-humidity map:
0 69 1
1 0 69

humidity-to-location map:
60 56 37
56 93 4
"""


@dataclass(frozen=True)
class Range:
    start: int
    size: int

    @cached_property
    def finish(self) -> int:
        return self.start + self.size - 1

    def to_set(self) -> set[int]:
        return set(range(self.start, self.start + self.size))

    def __contains__(self, item: int) -> bool:
        return self.start <= item < self.start + self.size

    def disjoint(self, other: Range) -> bool:
        return self.start > other.finish or other.start > self.finish

    def intersect(self, range_: Range) -> Range | None:
        if self.disjoint(range_):
            return None
        if self.start >= range_.start:
            return Range(self.start, min(range_.finish - self.start + 1, self.size))
        return Range(range_.start, min(self.finish - range_.start + 1, range_.size))

    @classmethod
    def from_start_and_finish(cls, start: int, finish: int) -> Range:
        return Range(start, size=finish - start + 1)

    def subtract(self, range_: Range) -> set[Range]:
        if self == range_:
            return set()
        if self.disjoint(range_):
            return {self}
        if self.start == range_.start:
            return {Range.from_start_and_finish(range_.finish + 1, self.finish)}
        if range_.finish == self.finish and self.start < range_.start:
            return {Range.from_start_and_finish(self.start, range_.start - 1)}
        return {Range.from_start_and_finish(self.start, range_.start - 1), Range.from_start_and_finish(range_.finish + 1, self.finish)}


@dataclass(frozen=True)
class NumberMapLine:
    dest: int
    range_: Range

    @classmethod
    def from_list(cls, input_: list[int]) -> NumberMapLine:
        return NumberMapLine(dest=input_[0], range_=Range(input_[1], input_[2]))

    def __getitem__(self, item: int) -> int:
        if item in self:
            return item + (self.dest - self.range_.start)
        raise KeyError

    def __contains__(self, item) -> bool:
        return item in self.range_

    def intersect(self, range_: Range) -> Range | None:
        return self.range_.intersect(range_)


class NumberMap:
    def __init__(
        self,
        maps: tuple[NumberMapLine, ...],
    ):
        self._maps = maps

    def __eq__(self, other) -> bool:
        if not isinstance(other, NumberMap):
            return False
        return self._maps == other._maps

    def __hash__(self) -> int:
        return hash(self._maps)

    def __getitem__(self, item: int) -> int:
        for map in self._maps:
            if item in map:
                return map[item]
        return item

    def apply_to_range(self, range_: Range) -> set[Range]:
        return {Range(self[range_.start], range_.size)}


def apply_number_map(number_maps: tuple[NumberMap, ...], item: int) -> int:
    result = item
    for number_map_ in number_maps:
        result = number_map_[result]
    return result


def lowest_location(to_parse: str) -> int:
    seeds_line, _, remainder = to_parse.split('\n', 2)
    seed_numbers: set[int] = set.union(*[range_.to_set() for range_ in seeds(seeds_line).result])
    number_maps_ = number_maps(remainder.replace('\n\n', '|')[:-1]).result

    locations = {
        apply_number_map(number_maps_, seed)
        for seed in seed_numbers
    }
    return min(locations)


range_ = and_(integer, right(word(' '), integer), Range)
seeds = apply(set, right(word("seeds: "), separated_by(range_, ' ')))

number_map_line = apply(NumberMapLine.from_list, separated_by(integer, ' '))
number_map_lines = apply(
    lambda x: NumberMap(tuple(x)),
    separated_by(number_map_line, '\n')
)

thingy = or_(*map(word, ['soil', 'seed', 'humidity', 'fertilizer', 'location', 'water', 'light', 'temperature']))
number_map_header = and_(and_(and_(thingy, word('-to-')), thingy), word(' map:\n'))
number_map = right(number_map_header, number_map_lines)
number_maps = apply(tuple, separated_by(number_map, '|'))


assert seeds("seeds: 79 3 55 1").result == {Range(79, 3), Range(55, 1)}
assert number_map_line("60 56 2").result == NumberMapLine(60, Range(56, 2))
assert number_map("humidity-to-location map:\n60 56 37").result == NumberMap((NumberMapLine(60, Range(56, 37)),)),number_map("humidity-to-location map:\n60 56 37").result
assert number_map("humidity-to-location map:\n60 56 37\n9 9 9").result == NumberMap((NumberMapLine(60, Range(56, 37)), NumberMapLine(9, Range(9, 9)),))
assert number_map("humidity-to-location map:\n60 56 37\n9 9 9").result == NumberMap((NumberMapLine(60, Range(56, 37)), NumberMapLine(9, Range(9, 9)),))
assert number_map("water-to-location map:\n60 56 37\n9 9 9").result == NumberMap((NumberMapLine(60, Range(56, 37)), NumberMapLine(9, Range(9, 9)),))
assert number_map("seed-to-soil map:\n60 56 37\n9 9 9").result == NumberMap((NumberMapLine(60, Range(56, 37)), NumberMapLine(9, Range(9, 9)),))
assert number_maps("water-to-location map:\n60 56 37\n9 9 9|seed-to-soil map:\n9 9 9").result == (
    NumberMap(
        (NumberMapLine(60, Range(56, 37)), NumberMapLine(9, Range(9, 9)),)
    ),
    NumberMap(
        (NumberMapLine(9, Range(9, 9)),)
    ),
)
assert NumberMap(tuple())[1000] == 1000
assert NumberMap((NumberMapLine(60, Range(56, 37)),))[56] == 60, NumberMap((NumberMapLine(60, Range(56, 37)),))[56]
assert NumberMap((NumberMapLine(60, Range(56, 37)),))[1000] == 1000
assert NumberMap((NumberMapLine(60, Range(56, 2)),))[58] == 58
assert NumberMap((NumberMapLine(60, Range(56, 2)),))[57] == 61

number_map_line_1 = NumberMapLine(60, Range(56, 2))
number_map_1 = NumberMap((number_map_line_1,))
number_map_2 = NumberMap((NumberMapLine(90, Range(61, 2)),))
assert apply_number_map((NumberMap(tuple()),), 9) == 9
assert apply_number_map((number_map_1,), 56) == 60
assert apply_number_map((number_map_1, number_map_2), 56) == 60
assert apply_number_map((number_map_1, number_map_2), 57) == 90

assert number_map_line_1.intersect(Range(56, 2)) == Range(56, 2)
assert number_map_line_1.intersect(Range(55, 1)) == None
assert number_map_line_1.intersect(Range(90, 1)) == None
assert number_map_line_1.intersect(Range(55, 2)) == Range(56, 1)
assert number_map_line_1.intersect(Range(56, 3)) == Range(56, 2)
assert number_map_line_1.intersect(Range(57, 2)) == Range(57, 1)

assert Range(50, 3).subtract(Range(50, 3)) == set()
assert Range(50, 3).subtract(Range(50, 2)) == {Range(52, 1)}, Range(50, 3).subtract(Range(50, 2))
assert Range(50, 3).subtract(Range(51, 2)) == {Range(50, 1)}
assert Range(50, 3).subtract(Range(90, 1)) == {Range(50, 3)}
assert Range(50, 3).subtract(Range(51, 1)) == {Range(50, 1), Range(52, 1)}

assert number_map_1.apply_to_range(Range(56, 1)) == {Range(60, 1)}
assert number_map_1.apply_to_range(Range(56, 1)) == {Range(60, 1)}
assert number_map_1.apply_to_range(Range(30, 1)) == {Range(30, 1)}
assert number_map_1.apply_to_range(Range(55, 2)) == {Range(55, 1), Range(60, 1)}

assert lowest_location(example_data) == 46

# with open('day5_input', 'r') as f:
#     data = f.read()
#
# print(lowest_location(data))
