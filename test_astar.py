
import unittest
from math import inf

from grid import GridWorld
from astar import astar, heuristic
from dijkstra import dijkstra


class AStarTests(unittest.TestCase):

    def test_open_grid_optimal(self):
        world = GridWorld(
            rows=5,
            cols=7,
            start=(0, 0),
            goal=(4, 6)
        )

        result = astar(world)

        self.assertTrue(result.found)
        self.assertEqual(result.cost, 10)
        self.assertEqual(len(result.path), 11)
        self.assertEqual(result.path[0], world.start)
        self.assertEqual(result.path[-1], world.goal)

    def test_detour(self):
        world = GridWorld(
            rows=5,
            cols=5,
            start=(2, 0),
            goal=(2, 4),
            obstacles={(2, 1), (2, 2), (2, 3)}
        )

        result = astar(world)

        self.assertTrue(result.found)
        self.assertEqual(result.cost, 6)

    def test_unreachable(self):
        world = GridWorld(
            rows=3,
            cols=3,
            start=(0, 0),
            goal=(2, 2),
            obstacles={(0, 1), (1, 0)}
        )

        result = astar(world)

        self.assertFalse(result.found)
        self.assertEqual(result.path, [])
        self.assertEqual(result.cost, inf)

    def test_matches_dijkstra(self):
        worlds = [
            GridWorld(rows=5, cols=5, start=(0, 0), goal=(4, 4)),
            GridWorld(
                rows=5,
                cols=5,
                start=(2, 0),
                goal=(2, 4),
                obstacles={(2, 1), (2, 2), (2, 3)}
            ),
            GridWorld(
                rows=6,
                cols=6,
                start=(0, 0),
                goal=(5, 5),
                obstacles={(1, 1), (1, 2), (2, 2), (3, 2)}
            )
        ]

        for world in worlds:
            astar_result = astar(world)
            dijkstra_result = dijkstra(world)

            self.assertEqual(
                astar_result.found,
                dijkstra_result.found
            )

            self.assertEqual(
                astar_result.cost,
                dijkstra_result.cost
            )

    def test_manhattan_heuristic(self):
        self.assertEqual(
            heuristic((0, 0), (4, 6)),
            10
        )

        self.assertEqual(
            heuristic((2, 3), (2, 3)),
            0
        )


if __name__ == "__main__":
    unittest.main()
