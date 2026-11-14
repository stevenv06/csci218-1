
import math
import unittest
from grid import GridWorld
from dijkstra import dijkstra


class GridTests(unittest.TestCase):
    def test_boundary_and_four_neighbours(self):
        world = GridWorld(3, 3, (0, 0), (2, 2))
        self.assertEqual(set(world.neighbors((0, 0))), {(0, 1), (1, 0)})
        self.assertEqual(set(world.neighbors((1, 1))), {(0, 1), (1, 2), (2, 1), (1, 0)})

    def test_protect_endpoints(self):
        world = GridWorld(3, 3, (0, 0), (2, 2))
        self.assertFalse(world.toggle_obstacle((0, 0)))
        self.assertFalse(world.set_goal((0, 0)))
        self.assertFalse(world.toggle_obstacle((-1, 0)))

    def test_invalid_world(self):
        with self.assertRaises(ValueError):
            GridWorld(2, 2, (0, 0), (1, 1), {(0, 0)})


class DijkstraTests(unittest.TestCase):
    def assert_valid_path(self, world, path):
        self.assertEqual(path[0], world.start)
        self.assertEqual(path[-1], world.goal)
        for u, v in zip(path, path[1:]):
            self.assertIn(v, set(world.neighbors(u)))

    def test_open_grid_optimal(self):
        world = GridWorld(5, 7, (0, 0), (4, 6))
        result = dijkstra(world)
        self.assertTrue(result.found)
        self.assertEqual(result.cost, 10)
        self.assertEqual(len(result.path), 11)
        self.assert_valid_path(world, result.path)

    def test_detour(self):
        world = GridWorld(5, 5, (2, 0), (2, 4), {(2, 1), (2, 2), (2, 3)})
        result = dijkstra(world)
        self.assertEqual(result.cost, 6)
        self.assert_valid_path(world, result.path)

    def test_unreachable(self):
        world = GridWorld(3, 3, (0, 0), (2, 2), {(0, 1), (1, 0)})
        result = dijkstra(world)
        self.assertFalse(result.found)
        self.assertEqual(result.path, [])
        self.assertTrue(math.isinf(result.cost))
        self.assertEqual(result.nodes_expanded, 1)

    def test_consistency(self):
        world = GridWorld(4, 4, (0, 0), (3, 3), {(1, 1), (2, 1)})
        a, b = dijkstra(world), dijkstra(world)
        self.assertEqual(a.path, b.path)
        self.assertEqual(a.nodes_expanded, b.nodes_expanded)
        self.assertEqual(a.nodes_expanded, len(a.explored_order))


if __name__ == '__main__':
    unittest.main()
