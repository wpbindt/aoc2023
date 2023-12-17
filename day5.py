from __future__ import annotations

from interval import Interval, explode
from parsing import *

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


def lowest_location(to_parse: str) -> int:
    pass


interval = and_(integer, right(word(' '), integer), Interval.from_start_and_size)
seeds = apply(set, right(word("seeds: "), separated_by(interval, ' ')))

number_map_line: Parser[dict[Interval, int]] = apply(lambda ints: {Interval.from_start_and_size(ints[1], ints[2]): ints[0]}, separated_by(integer, ' '))
number_map_lines = apply(
    lambda x: {interval_: offset for line in x for interval_, offset in line.items()},
    separated_by(number_map_line, '\n')
)

NumberMap = dict[Interval, int]
thingy = or_(*map(word, ['soil', 'seed', 'humidity', 'fertilizer', 'location', 'water', 'light', 'temperature']))
number_map_header = and_(and_(and_(thingy, word('-to-')), thingy), word(' map:\n'))
number_map: Parser[NumberMap] = right(number_map_header, number_map_lines)
number_maps = apply(tuple, separated_by(number_map, '|'))


def apply_number_map(number_map: NumberMap, interval: Interval) -> set[Interval]:
    sub_intervals = explode(interval, intervals_to_explode_by=set(number_map))
    return {
        apply_number_map_to_sub_interval(number_map, sub_interval)
        for sub_interval in sub_intervals
    }


def apply_number_map_to_sub_interval(number_map: NumberMap, interval: Interval) -> Interval:
    for map_interval, offset in number_map.items():
        if not map_interval.disjoint(interval):
            return interval.move(offset)
    return interval


assert seeds("seeds: 79 3 55 1").result == {Interval(79, 81), Interval(55, 55)}
assert number_map_line("60 56 2").result == {Interval(56, 57): 60}
assert number_map("humidity-to-location map:\n60 56 37").result == {Interval(56, 92): 60}
assert number_maps("water-to-location map:\n60 56 37\n9 9 9|seed-to-soil map:\n9 9 9").result == (
    {Interval(56, 92): 60, Interval(9, 17): 9},
    {Interval(9, 17): 9},
), number_maps("water-to-location map:\n60 56 37\n9 9 9|seed-to-soil map:\n9 9 9").result

assert apply_number_map(dict(), Interval(3, 9)) == {Interval(3, 9)}
assert apply_number_map({Interval(3, 9): 1}, Interval(3, 9)) == {Interval(4, 10)}
assert apply_number_map({Interval(3, 9): 1}, Interval(3, 9)) == {Interval(4, 10)}
assert apply_number_map({Interval(100, 101): 1}, Interval(3, 9)) == {Interval(3, 9)}
assert apply_number_map({Interval(3, 4): 1}, Interval(3, 9)) == {Interval(4, 5), Interval(5, 9)}

assert lowest_location(example_data) == 46, lowest_location(example_data)
