from __future__ import annotations

from enum import Enum
from typing import TypeVar, Generic, Callable, Hashable, Optional, Iterator
from uuid import uuid4

T = TypeVar('T')


class Node(Generic[T]):
    def __init__(self, payload: T, id_: Optional[Hashable] = None) -> None:
        self.payload = payload
        self.id = id_ or uuid4()
        self.traversal_state = TraversalState.UNDISCOVERED

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: Node[T]) -> bool:
        return hash(self) == hash(other)


class TraversalState(Enum):
    PROCESSED = 0
    DISCOVERED = 1
    UNDISCOVERED = 2

NodeId = Hashable

class Graph(Generic[T]):
    def __init__(self, nodes: set[Node[T]]) -> None:
        self._nodes: dict[NodeId, Node[T]] = {node.id: node for node in nodes}
        self._edges: dict[NodeId, set[Node[T]]] = {node.id: set() for node in nodes}

    def insert_edge(
        self,
        node_1: NodeId,
        node_2: NodeId,
    ) -> None:
        self._edges[node_1].add(self._nodes[node_2])
        self._edges[node_2].add(self._nodes[node_1])

    def traverse_from(
        self,
        start: NodeId,
    ) -> Iterator[Node[T]]:
        discovered_nodes: set[Node[T]] = {self._nodes[start]}
        while len(discovered_nodes) > 0:
            current = discovered_nodes.pop()
            yield current

            for connecting_node in self._edges[current.id]:
                if connecting_node.traversal_state != TraversalState.UNDISCOVERED:
                    continue
                connecting_node.traversal_state = TraversalState.DISCOVERED
                discovered_nodes.add(connecting_node)
            current.traversal_state = TraversalState.PROCESSED


def graph_from_grid(
    grid: list[list[bool]],
    payload_factory: Callable[[], T]
) -> Graph[T]:
    nodes = dict()
    for y, row in enumerate(grid):
        for x, element in enumerate(row):
            if not element:
                continue
            node = Node(payload=payload_factory())
            nodes[(x, y)] = node
    graph = Graph(set(nodes.values()))
    for coordinates, node in nodes.items():
        x, y = coordinates
        for neighbor in {(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)}:
            if neighbor not in nodes:
                continue
            graph.insert_edge(node, nodes[neighbor])

    return graph
