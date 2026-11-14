
from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from math import inf
from time import perf_counter
from grid import Cell, GridWorld


@dataclass
class SearchResult:
    path: list[Cell]
    cost: float
    explored_order: list[Cell]
    nodes_expanded: int
    elapsed_ms: float
    found: bool


def dijkstra(world: GridWorld) -> SearchResult:
    """Return optimal path and metrics, or no path with cost=inf.

    Dijkstra settles each cell once when popped with its minimum known distance.
    A heap provides O((V + E) log V) time and O(V + E) memory in this
    grid representation (E <= 4V). Time excludes UI animation.
    """
    started = perf_counter()
    source, target = world.start, world.goal
    distances: dict[Cell, float] = {source: 0.0}
    predecessor: dict[Cell, Cell] = {}
    visited: set[Cell] = set()
    explored: list[Cell] = []
    sequence = count()
    frontier: list[tuple[float, int, Cell]] = [(0.0, next(sequence), source)]

    while frontier:
        distance, _, current = heappop(frontier)
        if current in visited or distance > distances.get(current, inf):
            continue  # stale heap item
        visited.add(current)
        explored.append(current)
        if current == target:
            path = [target]
            while path[-1] != source:
                path.append(predecessor[path[-1]])
            path.reverse()
            return SearchResult(path, distance, explored, len(explored),
                                (perf_counter() - started) * 1000, True)
        for neighbor in world.neighbors(current):
            if neighbor in visited:
                continue
            alternative = distance + 1.0
            if alternative < distances.get(neighbor, inf):
                distances[neighbor] = alternative
                predecessor[neighbor] = current
                heappush(frontier, (alternative, next(sequence), neighbor))

    return SearchResult([], inf, explored, len(explored),
                        (perf_counter() - started) * 1000, False)
