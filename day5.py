from __future__ import annotations
from functools import lru_cache

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
class NumberMapLine:
    dest: int
    source: int
    range_: int

    @classmethod
    def from_list(cls, input_: list[int]) -> NumberMapLine:
        return NumberMapLine(dest=input_[0], source=input_[1], range_=input_[2])

    def to_dict(self) -> dict[int, int]:
        return {
            self.source + offset: self.dest + offset
            for offset in range(self.range_)
        }

    def __getitem__(self, item: int) -> int:
        if item in self:
            return item + (self.dest - self.source)
        raise KeyError

    def __contains__(self, item) -> bool:
        return self.source <= item < self.source + self.range_


def compose(dict1: dict[int, int], dict2: dict[int, int]) -> dict[int, int]:
    result = {
                 k: dict2.get(dict1[k], dict1[k])
                 for k in dict1
             } | {
                 k: v
                 for k, v in dict2.items()
                 if k not in dict1
             }

    return result


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


def apply_number_map(number_maps: tuple[NumberMap, ...], item: int) -> int:
    result = item
    for number_map_ in number_maps:
        result = number_map_[result]
    print(result)
    return result


def lowest_location(to_parse: str) -> int:
    print(1)
    seeds_line, _, remainder = to_parse.split('\n', 2)
    print(2)
    seed_numbers: set[int] = seeds(seeds_line).result
    print(3)
    number_maps_ = number_maps(remainder.replace('\n\n', '|')[:-1]).result

    locations = {
        apply_number_map(number_maps_, seed)
        for seed in seed_numbers
    }
    return min(locations)


seeds = apply(set, right(word("seeds: "), separated_by(integer, ' ')))

number_map_line = apply(NumberMapLine.from_list, separated_by(integer, ' '))
number_map_lines = apply(
    lambda x: NumberMap(tuple(x)),
    separated_by(number_map_line, '\n')
)

thingy = or_(*map(word, ['soil', 'seed', 'humidity', 'fertilizer', 'location', 'water', 'light', 'temperature']))
number_map_header = and_(and_(and_(thingy, word('-to-')), thingy), word(' map:\n'))
number_map = right(number_map_header, number_map_lines)
number_maps = apply(tuple, separated_by(number_map, '|'))


assert seeds("seeds: 79 14 55 13").result == {79, 14, 55, 13}
assert number_map_line("60 56 2").result == NumberMapLine(60, 56, 2)
assert number_map("humidity-to-location map:\n60 56 37").result == NumberMap((NumberMapLine(60, 56, 37),)),number_map("humidity-to-location map:\n60 56 37").result
assert number_map("humidity-to-location map:\n60 56 37\n9 9 9").result == NumberMap((NumberMapLine(60, 56, 37), NumberMapLine(9, 9, 9),))
assert number_map("humidity-to-location map:\n60 56 37\n9 9 9").result == NumberMap((NumberMapLine(60, 56, 37), NumberMapLine(9, 9, 9),))
assert number_map("water-to-location map:\n60 56 37\n9 9 9").result == NumberMap((NumberMapLine(60, 56, 37), NumberMapLine(9, 9, 9),))
assert number_map("seed-to-soil map:\n60 56 37\n9 9 9").result == NumberMap((NumberMapLine(60, 56, 37), NumberMapLine(9, 9, 9),))
assert number_maps("water-to-location map:\n60 56 37\n9 9 9|seed-to-soil map:\n9 9 9").result == (
    NumberMap(
        (NumberMapLine(60, 56, 37), NumberMapLine(9, 9, 9),)
    ),
    NumberMap(
        (NumberMapLine(9, 9, 9),)
    ),
)
assert NumberMap(tuple())[1000] == 1000
assert NumberMap((NumberMapLine(60, 56, 37),))[56] == 60, NumberMap((NumberMapLine(60, 56, 37),))[56]
assert NumberMap((NumberMapLine(60, 56, 37),))[1000] == 1000
assert NumberMap((NumberMapLine(60, 56, 2),))[58] == 58
assert NumberMap((NumberMapLine(60, 56, 2),))[57] == 61

number_map_1 = NumberMap((NumberMapLine(60, 56, 2),))
number_map_2 = NumberMap((NumberMapLine(90, 61, 2),))
assert apply_number_map((NumberMap(tuple()),), 9) == 9
assert apply_number_map((number_map_1,), 56) == 60
assert apply_number_map((number_map_1, number_map_2), 56) == 60
assert apply_number_map((number_map_1, number_map_2), 57) == 90
assert lowest_location(example_data) == 35

assert compose({}, {}) == {}
assert compose({1: 2}, {}) == {1: 2}
assert compose({1: 2}, {3: 4}) == {1: 2, 3: 4}
assert compose({1: 2, 3: 5}, {3: 4}) == {1: 2, 3: 5}, compose({1: 2, 3: 5}, {3: 4})
assert compose({1: 9, 2: 10}, {3: 4}) == {1: 9, 2: 10, 3: 4}
assert compose({1: 9, 2: 10, 3: 11}, {3: 4}) == {1: 9, 2: 10, 3: 11}
assert compose({1: 9, 2: 10, 3: 11}, {10: 1000}) == {1: 9, 2: 1000, 3: 11, 10: 1000}, compose({1: 9, 2: 10, 3: 11}, {10: 1000})

with open('day5_input', 'r') as f:
    data = f.read()

print(lowest_location(data))
