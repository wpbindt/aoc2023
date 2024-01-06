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
    def __init__(self, delta: GridCoordinate, repr: str = '*') -> None:
        self._delta = delta
        self._repr = repr

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
            return Direction(self._delta + other._delta, repr=self._repr + other._repr)
        return other + self._delta

    def __eq__(self, other: Direction) -> bool:
        return self._delta == other._delta

    def __repr__(self) -> str:
        return self._repr

    def __hash__(self) -> int:
        return hash(self._delta)


north = Direction(GridCoordinate(0, -1), 'N')
south = Direction(GridCoordinate(0, 1), 'S')
west = Direction(GridCoordinate(-1, 0), 'W')
east = Direction(GridCoordinate(1, 0), 'E')
north_east = north + east
north_west = north + west
south_west = south + west
south_east = south + east
all_directions = {north, south, east, west, north_west, north_east, south_west, south_east}


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


def get_vertical_edge_coordinates(grid: list[list[typing.Any]]) -> Iterator[GridCoordinate]:
    height = len(grid)
    width = len(grid[0])
    for y in range(height):
        yield GridCoordinate(x=0, y=y)
        yield GridCoordinate(x=width - 1, y=y)


def get_horizontal_edge_coordinates(grid: list[list[typing.Any]]) -> Iterator[GridCoordinate]:
    height = len(grid)
    width = len(grid[0])
    for x in range(width):
        yield GridCoordinate(x=x, y=0)
        yield GridCoordinate(x=x, y=height - 1)


def get_edges(grid: list[list[ConnectingGridElement]]) -> Iterator[tuple[GridCoordinate, GridCoordinate]]:
    for coordinate, element in iterate_grid(grid):
        for connecting_direction in element.connecting_directions:
            neighbor = get_neighbor(grid, coordinate, connecting_direction)
            if neighbor is None:
                continue
            if connecting_direction.opposite() in neighbor.connecting_directions:
                relevants = {coordinate, connecting_direction + coordinate}
                assert len(relevants) > 1
                yield coordinate, connecting_direction + coordinate


def graph_from_connecting_grid_elements(
    grid: list[list[ConnectingGridElement]],
) -> Graph:
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


def main_2(to_parse: str, start_node: GridCoordinate) -> int:
    parsed = grid(to_parse)
    if isinstance(parsed, CouldNotParse):
        raise Exception
    loop_graph = graph_from_connecting_grid_elements(parsed.result)
    loop = {node.id for node in loop_graph.traverse_from(start_node)}

    new_grid = [[ConnectingGridElement(set()) for _ in row] for row in parsed.result]
    enc = {
        coordinate
        for coordinate in loop
        if east + coordinate in loop and not loop_graph.has_edge(coordinate, east + coordinate)
    }
    wnc = {
        coordinate
        for coordinate in loop
        if west + coordinate in loop and not loop_graph.has_edge(coordinate, west + coordinate)
    }
    nnc = {
        coordinate
        for coordinate in loop
        if north + coordinate in loop and not loop_graph.has_edge(coordinate, north + coordinate)
    }
    snc = {
        coordinate
        for coordinate in loop
        if south + coordinate in loop and not loop_graph.has_edge(coordinate, south + coordinate)
    }
    hnc = enc | wnc
    vnc = snc | nnc

    for coordinate, element in iterate_grid(new_grid):
        if coordinate not in loop:
            element.connecting_directions.update({
                direction
                for direction in all_directions
            })
            continue
        if coordinate in nnc:
            element.connecting_directions.update({
                west, east, north_west, north_east
            })
        if coordinate in snc:
            element.connecting_directions.update({
                west, east, south_west, south_east
            })
        if coordinate in enc:
            element.connecting_directions.update({
                north, south, south_east, north_east
            })
        if coordinate in wnc:
            element.connecting_directions.update({
                north, south, south_west, north_west
            })

    outsides = set()
    graph = graph_from_connecting_grid_elements(new_grid)
    for coordinate in get_horizontal_edge_coordinates(new_grid):
        if coordinate in loop and coordinate not in hnc:
            continue
        for node in graph.traverse_from(coordinate):
            outsides.add(node.id)
    for coordinate in get_vertical_edge_coordinates(new_grid):
        if coordinate in loop and coordinate not in vnc:
            continue
        for node in graph.traverse_from(coordinate):
            outsides.add(node.id)
    all_coordinates = {coordinate for coordinate, _ in iterate_grid(new_grid)}
    return len(all_coordinates - (loop | outsides))


with open('day10_inputr', 'r') as f:
    to_parse = f.read()
    start_node = GridCoordinate(x=75, y=60)

example_data_3 = """..........
.S------7.
.|F----7|.
.||....||.
.||....||.
.|L-7F-J|.
.|..||..|.
.L--JL--J.
.........."""
example_data_2 = """S---7
|F-7|
||.||
|L7||
|.|||
L-JLJ"""
example_data = """S---7
|F-7|
||.||
|L7||
L-JLJ"""
start = perf_counter()
print(main_2(example_data_2, GridCoordinate(0, 0)))

print(perf_counter() - start)
