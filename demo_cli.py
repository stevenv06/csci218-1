"""No-GUI demonstration for quick validation and teammate integration."""
from grid import GridWorld
from dijkstra import dijkstra

if __name__ == '__main__':
    world = GridWorld(rows=6, cols=10, start=(0, 0), goal=(5, 9),
                      obstacles={(2, c) for c in range(9) if c != 7})
    answer = dijkstra(world)
    print(f'Found: {answer.found}; cost: {answer.cost}; expanded: {answer.nodes_expanded}; time: {answer.elapsed_ms:.4f} ms')
    route = set(answer.path)
    for row in range(world.rows):
        print(''.join('S' if (row, col) == world.start else
                      'G' if (row, col) == world.goal else
                      '#' if (row, col) in world.obstacles else
                      '*' if (row, col) in route else '.'
                      for col in range(world.cols)))
