from enum import Enum
from functools import partial
from typing import TypeVar, Iterator, Callable

from parsing import CouldNotParse, word, apply, or_, many, separated_by, parse

T = TypeVar('T')


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


def expand_rows(parsed_space: list[list[Space]]) -> list[list[Space]]:
    expanded_space = []
    for row in parsed_space:
        expanded_space.append(row.copy())
        if Space.GALAXY not in row:
            expanded_space.append(row.copy())
    return expanded_space


def get_empty_column_numbers(parsed_space: list[list[Space]]) -> Iterator[int]:
    yield from get_empty_row_numbers(transpose(parsed_space))


def get_empty_row_numbers(parsed_space: list[list[Space]]) -> Iterator[int]:
    yield from (
        index
        for index, row in enumerate(parsed_space)
        if Space.GALAXY not in row
    )


def expand_columns(parsed_space: list[list[Space]]) -> list[list[Space]]:
    return transpose(expand_rows(transpose(parsed_space)))


Coordinate = tuple[int, int]


def distance(coordinate_1: Coordinate, coordinate_2: Coordinate) -> int:
    x_distance = abs(coordinate_2[0] - coordinate_1[0])
    y_distance = abs(coordinate_2[1] - coordinate_1[1])
    return x_distance + y_distance


def get_galaxy_coordinates(parsed_space: list[list[Space]]) -> set[Coordinate]:
    return {
        (x, y)
        for y, row in enumerate(parsed_space)
        for x, space_tile in enumerate(row)
        if space_tile == Space.GALAXY
    }


def pairs(my_set: set[T]) -> Iterator[tuple[T, T]]:
    ordered_set = list(my_set)
    for index, element in enumerate(ordered_set):
        for other_element in ordered_set[index:]:
            yield element, other_element


def compose(*fs: Callable) -> Callable:
    if len(fs) == 1:
        return fs[0]
    f, *remaining_fs = fs
    return lambda *args, **kwargs: f(compose(*remaining_fs)(*args, **kwargs))


def main(to_parse: str) -> int:
    return compose(
        sum,
        partial(map, lambda x: distance(*x)),
        pairs,
        get_galaxy_coordinates,
        expand_rows,
        expand_columns,
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

assert expand_rows([]) == []
assert expand_rows([[Space.NOTHING]]) == 2 * [[Space.NOTHING]]
assert expand_rows([[Space.GALAXY]]) == [[Space.GALAXY]]

assert expand_columns([]) == []
assert expand_columns([[Space.GALAXY]]) == [[Space.GALAXY]]
assert expand_columns([[Space.NOTHING]]) == [[Space.NOTHING, Space.NOTHING]]

assert distance((1, 1), (1, 1)) == 0
assert distance((1, 1), (1, 2)) == 1
assert distance((1, 2), (1, 1)) == 1
assert distance((2, 1), (1, 1)) == 1
assert distance((2, 2), (1, 1)) == 2

assert get_galaxy_coordinates([[Space.NOTHING]]) == set()
assert get_galaxy_coordinates([[Space.NOTHING, Space.GALAXY]]) == {(1, 0)}

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

assert main(example_data) == 374, main(example_data)

with open('day11_input') as f:
    to_parse = f.read()


# print(main(to_parse))
