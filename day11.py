from enum import Enum
from functools import partial
from itertools import count, repeat, combinations
from time import perf_counter
from typing import TypeVar, Iterator, Callable

from parsing import CouldNotParse, word, apply, or_, many, separated_by, parse

T = TypeVar('T')

EXPANSION = 1_000_000


class Space(Enum):
    GALAXY = 1
    NOTHING = 2


def transpose(matrix: list[list[T]]) -> list[list[T]]:
    height = len(matrix)
    if height == 0:
        return []
    width = len(matrix[0])
    return [
        [
            matrix[y][x]
            for y in range(height)
        ]
        for x in range(width)
    ]


galaxy = apply(lambda x: Space.GALAXY, word('#'))
nothing = apply(lambda x: Space.NOTHING, word('.'))
space = or_(nothing, galaxy)
space_row = many(space)
space_document = separated_by(space_row, '\n')


def get_empty_column_numbers(parsed_space: list[list[Space]]) -> Iterator[int]:
    yield from get_empty_row_numbers(transpose(parsed_space))


def get_empty_row_numbers(parsed_space: list[list[Space]]) -> Iterator[int]:
    yield from (
        index
        for index, row in enumerate(parsed_space)
        if Space.GALAXY not in row
    )


Coordinate = tuple[int, int]


def distance(coordinate_1: Coordinate, coordinate_2: Coordinate) -> int:
    x_distance = abs(coordinate_2[0] - coordinate_1[0])
    y_distance = abs(coordinate_2[1] - coordinate_1[1])
    return x_distance + y_distance


def right_pad(iterator: Iterator[T]) -> Iterator[T | None]:
    yield from iterator
    while True:
        yield None


def pad(indices_to_yield_at: Iterator[int], iterator: Iterator[T]) -> Iterator[T | None]:
    current_index_iterator = count()
    for index_to_yield_at, element in zip(indices_to_yield_at, iterator):
        for current_index in current_index_iterator:
            if current_index == index_to_yield_at:
                break
            yield None
        yield element


def expanded_enumerate(iterator: Iterator[T], expansions: Iterator[int]) -> Iterator[tuple[int, T]]:
    total_expansion = 0
    for index, expansion, element in zip(count(), expansions, iterator):
        total_expansion += expansion
        yield index + total_expansion, element


def get_expansions(expansion_points: Iterator[int], expansion: int) -> Iterator[int]:
    yield from map(
        lambda x: 0 if x is None else x,
        right_pad(
            pad(
                indices_to_yield_at=expansion_points,
                iterator=repeat(expansion)
            ),
        )
    )


def get_galaxy_coordinates(parsed_space: list[list[Space]], expansion: int) -> Iterator[Coordinate]:
    t_parsed_space = transpose(parsed_space)
    row_expansions = get_expansions(get_empty_column_numbers(parsed_space), expansion=expansion)
    for y, row in expanded_enumerate(t_parsed_space, expansions=row_expansions):
        column_expansions = get_expansions(get_empty_row_numbers(parsed_space), expansion=expansion)
        for x, element in expanded_enumerate(row, expansions=column_expansions):
            if element == Space.GALAXY:
                yield x, y


def pairs(my_set: Iterator[T]) -> Iterator[tuple[T, T]]:
    yield from combinations(my_set, 2)


def compose(*fs: Callable) -> Callable:
    if len(fs) == 1:
        return fs[0]
    f, *remaining_fs = fs
    return lambda *args, **kwargs: f(compose(*remaining_fs)(*args, **kwargs))


def main(to_parse: str) -> int:
    return main_2(to_parse, expansion=1)


def main_2(to_parse: str, expansion: int) -> int:
    return compose(
        sum,
        partial(map, lambda x: distance(*x)),
        pairs,
        partial(get_galaxy_coordinates, expansion=expansion),
        parse(space_document),
    )(to_parse)


assert transpose([]) == []
assert transpose([
    [0, 1],
    [0, 1],
]) == [
    [0, 0],
    [1, 1],
]
assert transpose([
    [0, 1],
]) == [[0], [1]]

assert galaxy('.').result == CouldNotParse()
assert galaxy('#').result == Space.GALAXY
assert nothing('#').result == CouldNotParse()
assert nothing('.').result == Space.NOTHING
assert space('.').result == Space.NOTHING
assert space('#').result == Space.GALAXY
assert space_row('#..#.').result == [Space.GALAXY, Space.NOTHING, Space.NOTHING, Space.GALAXY, Space.NOTHING]
assert space_document('#.#\n...').result == [
    [Space.GALAXY, Space.NOTHING, Space.GALAXY],
    [Space.NOTHING, Space.NOTHING, Space.NOTHING],
]

assert list(get_empty_row_numbers([])) == []
assert list(get_empty_row_numbers([
    [Space.NOTHING],
])) == [0]
assert list(get_empty_row_numbers([
    [Space.GALAXY],
])) == []

assert list(get_empty_column_numbers([])) == []
assert list(get_empty_column_numbers([
    [Space.NOTHING],
])) == [0]

assert distance((1, 1), (1, 1)) == 0
assert distance((1, 1), (1, 2)) == 1
assert distance((1, 2), (1, 1)) == 1
assert distance((2, 1), (1, 1)) == 1
assert distance((2, 2), (1, 1)) == 2

assert list(expanded_enumerate(iterator=iter('..#.'), expansions=iter([0, 1, 0, 1]))) == [(0, '.'), (2, '.'), (3, '#'), (5, '.')]
example_data = """...#......
.......#..
#.........
..........
......#...
.#........
.........#
..........
.......#..
#...#....."""

assert main(example_data) == 374, main(to_parse=example_data)
assert main_2(example_data, expansion=9) == 1030, main_2(example_data, expansion=9)
assert main_2(example_data, expansion=99) == 8410, main_2(example_data, expansion=99)

with open('day11_input') as f:
    to_parse = f.read()


start = perf_counter()
print(main_2(to_parse, expansion=999_999))
print(perf_counter() - start)
