from enum import Enum
from typing import TypeVar

from parsing import CouldNotParse, word, apply, or_, many, separated_by

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


def expand_columns(parsed_space: list[list[Space]]) -> list[list[Space]]:
    return transpose(expand_rows(transpose(parsed_space)))


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

assert expand_rows([]) == []
assert expand_rows([[Space.NOTHING]]) == 2 * [[Space.NOTHING]]
assert expand_rows([[Space.GALAXY]]) == [[Space.GALAXY]]

assert expand_columns([]) == []
assert expand_columns([[Space.GALAXY]]) == [[Space.GALAXY]]
assert expand_columns([[Space.NOTHING]]) == [[Space.NOTHING, Space.NOTHING]]
