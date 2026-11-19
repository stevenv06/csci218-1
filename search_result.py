"""Result returned by the A* search and displayed by the visualizer."""

from dataclasses import dataclass

from grid import Cell


@dataclass
class SearchResult:
    path: list[Cell]
    cost: float
    explored_order: list[Cell]
    nodes_expanded: int
    elapsed_ms: float
    found: bool
