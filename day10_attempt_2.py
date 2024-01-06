from __future__ import annotations

import typing
from dataclasses import dataclass
from time import perf_counter
from typing import Iterator, TypeVar

from graph import Graph, Node
from parsing import apply, word, Parser, or_, many, separated_by_, CouldNotParse


@dataclass(frozen=True)
class GridCoordinate:
    x: int
    y: int

    def __add__(self, other: GridCoordinate) -> GridCoordinate:
        return GridCoordinate(self.x + other.x, self.y + other.y)


class Direction:
    def __init__(self, delta: GridCoordinate) -> None:
        self._delta = delta

    def opposite(self) -> Direction:
        return Direction(GridCoordinate(x=-self._delta.x, y=-self._delta.y))

    @typing.overload
    def __add__(self, other: Direction) -> Direction:
        pass

    @typing.overload
    def __add__(self, other: GridCoordinate) -> GridCoordinate:
        pass

    def __add__(self, other):
        if isinstance(other, Direction):
            return Direction(self._delta + other._delta)
        return other + self._delta

    def __eq__(self, other: Direction) -> bool:
        return self._delta == other._delta

    def __hash__(self) -> int:
        return hash(self._delta)


north = Direction(GridCoordinate(0, -1))
south = north.opposite()
west = Direction(GridCoordinate(-1, 0))
east = west.opposite()


@dataclass(frozen=True)
class ConnectingGridElement:
    connecting_directions: set[Direction]


T = TypeVar('T')


def iterate_grid(grid: list[list[T]]) -> Iterator[tuple[GridCoordinate, T]]:
    for y, row in enumerate(grid):
        for x, element in enumerate(row):
            yield GridCoordinate(x, y), element


def get_element(grid: list[list[T]], coordinate: GridCoordinate) -> T | None:
    if -1 in {coordinate.x, coordinate.y}:
        return None
    try:
        return grid[coordinate.y][coordinate.x]
    except IndexError:
        return None


def get_neighbor(grid: list[list[T]], coordinate: GridCoordinate, direction: Direction) -> T | None:
    return get_element(grid, direction + coordinate)


def get_edges(grid: list[list[ConnectingGridElement]]) -> Iterator[tuple[GridCoordinate, GridCoordinate]]:
    for coordinate, element in iterate_grid(grid):
        for connecting_direction in element.connecting_directions:
            neighbor = get_neighbor(grid, coordinate, connecting_direction)
            if neighbor is None:
                continue
            if connecting_direction.opposite() in neighbor.connecting_directions:
                yield coordinate, connecting_direction + coordinate


def graph_from_connecting_grid_elements(grid: list[list[ConnectingGridElement]]) -> Graph:
    nodes = {
        Node(id_=coordinate, payload=None)
        for coordinate, _ in iterate_grid(grid)
    }
    graph = Graph(nodes=nodes)
    for edge in get_edges(grid):
        graph.insert_edge(*edge)

    return graph


north_south_pipe = apply(lambda x: ConnectingGridElement({north, south}), word('|'))
north_west_pipe = apply(lambda x: ConnectingGridElement({north, west}), word('J'))
north_east_pipe = apply(lambda x: ConnectingGridElement({north, east}), word('L'))
south_west_pipe = apply(lambda x: ConnectingGridElement({south, west}), word('7'))
south_east_pipe = apply(lambda x: ConnectingGridElement({south, east}), word('F'))
east_west_pipe = apply(lambda x: ConnectingGridElement({west, east}), word('-'))
pipe: Parser[ConnectingGridElement | None] = or_(
    north_south_pipe,
    north_west_pipe,
    north_east_pipe,
    south_west_pipe,
    south_east_pipe,
    east_west_pipe,
)
start = apply(lambda x: ConnectingGridElement({north, east, south, west}), word('S'))
nothing = apply(lambda x: ConnectingGridElement(set()), word('.'))
grid_element = or_(pipe, start, nothing)
grid_row = many(grid_element)
grid = separated_by_(grid_row, word('\n'))


def main(to_parse: str) -> int:
    parsed = grid(to_parse)
    if isinstance(parsed, CouldNotParse):
        raise Exception
    graph = graph_from_connecting_grid_elements(parsed.result)
    start_node = GridCoordinate(x=75, y=60)
    return len(list(graph.traverse_from(start_node))) // 2


with open('day10_inputr', 'r') as f:
    to_parse = f.read()

start = perf_counter()
print(main(to_parse))

print(perf_counter() - start)
