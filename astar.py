
"""Member 3: A* shortest-path search for a 4-connected unit-cost grid."""

from heapq import heappop, heappush
from itertools import count
from math import inf
from time import perf_counter

from grid import Cell, GridWorld
from search_result import SearchResult


def heuristic(current: Cell, goal: Cell) -> float:
    """
    Calculate Manhattan distance between two cells.

    This heuristic estimates the minimum number of moves
    required to reach the goal.
    """
    return abs(current[0] - goal[0]) + abs(current[1] - goal[1])


def astar(world: GridWorld) -> SearchResult:
    """
    Find the shortest path using the A* search algorithm.

    g(n) = Actual cost from the start to the current cell.
    h(n) = Estimated cost from the current cell to the goal.
    f(n) = g(n) + h(n).
    """

    started = perf_counter()

    source = world.start
    target = world.goal

    # Store the lowest known cost from the start to each cell.
    g_score = {source: 0.0}

    # Store the previous cell for reconstructing the final path.
    predecessor = {}

    # Track cells that have already been expanded.
    visited = set()
    explored = []

    # Prevent Python from comparing cell coordinates when priorities tie.
    sequence = count()

    # Add the starting cell to the priority queue.
    h_start = heuristic(source, target)

    frontier = [
        (h_start, h_start, next(sequence), 0.0, source)
    ]

    while frontier:

        # Get the cell with the lowest estimated total cost.
        f_score, h_score, _, distance, current = heappop(frontier)

        # Ignore outdated entries.
        if distance > g_score.get(current, inf):
            continue

        if current in visited:
            continue

        visited.add(current)
        explored.append(current)

        # Stop when the goal is reached.
        if current == target:

            path = [target]

            while path[-1] != source:
                path.append(predecessor[path[-1]])

            path.reverse()

            elapsed = (perf_counter() - started) * 1000

            return SearchResult(
                path=path,
                cost=distance,
                explored_order=explored,
                nodes_expanded=len(explored),
                elapsed_ms=elapsed,
                found=True
            )

        # Examine all legal neighbouring cells.
        for neighbor in world.neighbors(current):

            if neighbor in visited:
                continue

            # Every legal movement costs 1.
            tentative_g = distance + 1.0

            # Update the neighbour if a cheaper route is found.
            if tentative_g < g_score.get(neighbor, inf):

                g_score[neighbor] = tentative_g
                predecessor[neighbor] = current

                h = heuristic(neighbor, target)
                f = tentative_g + h

                heappush(
                    frontier,
                    (f, h, next(sequence), tentative_g, neighbor)
                )

    # No valid route was found.
    elapsed = (perf_counter() - started) * 1000

    return SearchResult(
        path=[],
        cost=inf,
        explored_order=explored,
        nodes_expanded=len(explored),
        elapsed_ms=elapsed,
        found=False
    )
