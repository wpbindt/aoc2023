from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from time import perf_counter
from typing import Iterator, TypeVar

from graph import Graph, Node
from parsing import apply, word, Parser, or_, many, separated_by_, CouldNotParse


@dataclass(frozen=True)
class GridCoordinate:
    x: int
    y: int


class Direction(ABC):
    @abstractmethod
    def opposite(self) -> Direction:
        pass

    @abstractmethod
    def __add__(self, other: GridCoordinate) -> GridCoordinate:
        pass


@dataclass(frozen=True)
class North(Direction):
    def __repr__(self) -> str:
        return 'N'

    def opposite(self) -> Direction:
        return South()

    def __add__(self, other: GridCoordinate) -> GridCoordinate:
        return GridCoordinate(x=other.x, y=other.y - 1)


@dataclass(frozen=True)
class South(Direction):
    def __repr__(self) -> str:
        return 'S'

    def opposite(self) -> Direction:
        return North()

    def __add__(self, other: GridCoordinate) -> GridCoordinate:
        return GridCoordinate(x=other.x, y=other.y + 1)


@dataclass(frozen=True)
class West(Direction):
    def __repr__(self) -> str:
        return 'W'

    def opposite(self) -> Direction:
        return East()

    def __add__(self, other: GridCoordinate) -> GridCoordinate:
        return GridCoordinate(x=other.x - 1, y=other.y)


@dataclass(frozen=True)
class East(Direction):
    def __repr__(self) -> str:
        return 'E'

    def opposite(self) -> Direction:
        return West()

    def __add__(self, other: GridCoordinate) -> GridCoordinate:
        return GridCoordinate(x=other.x + 1, y=other.y)


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


north_south = apply(lambda x: ConnectingGridElement({North(), South()}), word('|'))
north_west = apply(lambda x: ConnectingGridElement({North(), West()}), word('J'))
north_east = apply(lambda x: ConnectingGridElement({North(), East()}), word('L'))
south_west = apply(lambda x: ConnectingGridElement({South(), West()}), word('7'))
south_east = apply(lambda x: ConnectingGridElement({South(), East()}), word('F'))
east_west = apply(lambda x: ConnectingGridElement({West(), East()}), word('-'))
pipe: Parser[ConnectingGridElement | None] = or_(
    north_south,
    north_west,
    north_east,
    south_west,
    south_east,
    east_west,
)
start = apply(lambda x: ConnectingGridElement({North(), East(), South(), West()}), word('S'))
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
