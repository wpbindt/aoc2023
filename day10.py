from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator
from dataclasses import dataclass
from itertools import count

from parsing import or_, apply, word, many, separated_by_, Parser, CouldNotParse


@dataclass(frozen=True)
class NoNeighbor:
    pass


@dataclass(frozen=True)
class TooManyNeighbors:
    pass


id_counter = count()


class Node:
    def __init__(self) -> None:
        self.id = next(id_counter)
        self._neighbors = set()

    def add_neighbor(self, node: Node) -> None:
        self._neighbors.add(node)

    def go_to_neighbor_from(self, node: Node) -> Node | NoNeighbor | TooManyNeighbors:
        if node not in self._neighbors:
            raise Exception
        possible_directions = self._neighbors - {node}
        match len(possible_directions):
            case 1: return next(iter(possible_directions))
            case 0: return NoNeighbor()
            case _: return TooManyNeighbors()

    def traverse(self, neighbor: Node) -> Iterator[Node]:
        point1 = self
        point2 = neighbor
        yield point1
        while point2 != self:
            yield point2
            next_point2 = point2.go_to_neighbor_from(point1)
            point1, point2 = point2, next_point2

    def __repr__(self) -> str:
        neighbor_ids = str({neighbor.id for neighbor in self._neighbors})
        return f'Node({self.id}, {neighbor_ids})'


@dataclass(frozen=True)
class GridCoordinate:
    x: int
    y: int

    def __add__(self, other: GridCoordinate) -> GridCoordinate:
        return GridCoordinate(
            x=self.x + other.x,
            y=self.y + other.y,
        )

    def distance(self, other: GridCoordinate) -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def get_neighboring_coordinates(self) -> set[GridCoordinate]:
        return {
            self + GridCoordinate(0, 1),
            self + GridCoordinate(0, -1),
            self + GridCoordinate(-1, 0),
            self + GridCoordinate(1, 0),
        }


class Direction(ABC):
    @abstractmethod
    def get_delta(self) -> GridCoordinate:
        pass


class North(Direction):
    def get_delta(self) -> GridCoordinate:
        return GridCoordinate(0, -1)

    def __repr__(self) -> str:
        return 'N'


class South(Direction):
    def get_delta(self) -> GridCoordinate:
        return GridCoordinate(0, 1)

    def __repr__(self) -> str:
        return 'S'


class West(Direction):
    def get_delta(self) -> GridCoordinate:
        return GridCoordinate(-1, 0)

    def __repr__(self) -> str:
        return 'W'


class East(Direction):
    def get_delta(self) -> GridCoordinate:
        return GridCoordinate(1, 0)

    def __repr__(self) -> str:
        return 'E'


class ConnectingGridElement(ABC):
    @abstractmethod
    def get_connected_neighbors(self, start: GridCoordinate) -> set[GridCoordinate]:
        pass


@dataclass(frozen=True)
class Pipe(ConnectingGridElement):
    direction_1: Direction
    direction_2: Direction

    def get_connected_neighbors(self, start: GridCoordinate) -> set[GridCoordinate]:
        return {
            start + self.direction_1.get_delta(),
            start + self.direction_2.get_delta(),
        }


@dataclass(frozen=True)
class Start(ConnectingGridElement):
    def get_connected_neighbors(self, start: GridCoordinate) -> set[GridCoordinate]:
        return {
            start + North().get_delta(),
            start + South().get_delta(),
            start + East().get_delta(),
            start + West().get_delta(),
        }


north_south = apply(lambda x: Pipe(North(), South()), word('|'))
north_west = apply(lambda x: Pipe(North(), West()), word('J'))
north_east = apply(lambda x: Pipe(North(), East()), word('L'))
south_west = apply(lambda x: Pipe(South(), West()), word('7'))
south_east = apply(lambda x: Pipe(South(), East()), word('F'))
east_west = apply(lambda x: Pipe(West(), East()), word('-'))
pipe: Parser[ConnectingGridElement | None] = or_(
    north_south,
    north_west,
    north_east,
    south_west,
    south_east,
    east_west,
)
start = apply(lambda x: Start(), word('S'))
nothing = apply(lambda x: None, word('.'))
grid_element = or_(pipe, start, nothing)
grid_row = many(grid_element)
grid = separated_by_(grid_row, word('\n'))


class Grid:
    def __init__(self, map_: list[list[ConnectingGridElement | None]]) -> None:
        self._map = map_

    def connect(self, grid_coordinate_1: GridCoordinate, grid_coordinate_2: GridCoordinate) -> bool:
        if grid_coordinate_2.distance(grid_coordinate_1) != 1:
            return False

        grid_element_1 = self[grid_coordinate_1]
        grid_element_2 = self[grid_coordinate_2]

        if grid_element_1 is None or grid_element_2 is None:
            return False

        if grid_coordinate_2 not in grid_element_1.get_connected_neighbors(grid_coordinate_1):
            return False

        if grid_coordinate_1 not in grid_element_2.get_connected_neighbors(grid_coordinate_2):
            return False

        return True

    def __getitem__(self, item: GridCoordinate) -> ConnectingGridElement | None:
        try:
            return self._map[item.y][item.x]
        except IndexError:
            return None

    def start_coordinates(self) -> GridCoordinate:
        for y, row in enumerate(self._map):
            for x, element in enumerate(row):
                if isinstance(element, Start):
                    return GridCoordinate(x, y)


def make_nodes(grid_map: list[list[ConnectingGridElement | None]]) -> tuple[set[Node], Node]:
    pipe_grid = Grid(grid_map)
    nodes: dict[GridCoordinate, Node] = {
        GridCoordinate(x, y): Node()
        for y, row in enumerate(grid_map)
        for x, element in enumerate(row)
        if element is not None
    }
    for coordinate, node in nodes.items():
        for neighboring_coordinate in coordinate.get_neighboring_coordinates():
            if pipe_grid.connect(neighboring_coordinate, coordinate):
                neighboring_node = nodes.get(neighboring_coordinate)
                if neighboring_node is None:
                    continue
                node.add_neighbor(neighboring_node)

    return set(nodes.values()), nodes[pipe_grid.start_coordinates()]


example_data = '\n'.join([
    '.....',
    '.F-7.',
    '.|.|.',
    '.L-J.',
    '.....',
])


class Graph:
    def __init__(self, nodes: set[Node]) -> None:
        self._nodes = nodes


def main(to_parse: str) -> list[int]:
    parsed = grid(to_parse)
    if isinstance(parsed, CouldNotParse):
        raise Exception
    nodes, start_node = make_nodes(parsed.result)
    paths = []
    for neighbor in start_node._neighbors:
        paths.append(list(start_node.traverse(neighbor)))
    return [len(path) // 2 for path in paths]


with open('day10_inputr', 'r') as f:
    to_parse = f.read()

print(main(to_parse))
