"""Generate a static example pathfinding figure from actual Dijkstra output."""
from pathlib import Path
from grid import GridWorld
from dijkstra import dijkstra


def create_figure(output: str = 'example_result.png') -> None:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    world = GridWorld(10, 16, (1, 1), (8, 14),
                      {(r, 6) for r in range(8) if r != 4}
                      | {(6, c) for c in range(8, 14) if c != 10})
    result = dijkstra(world)
    fig, ax = plt.subplots(figsize=(10, 6.6))
    visited, path = set(result.explored_order), set(result.path)
    for r in range(world.rows):
        for c in range(world.cols):
            cell = (r, c)
            color = '#f1f5f9'
            if cell in visited: color = '#bfdbfe'
            if cell in world.obstacles: color = '#334155'
            if cell in path: color = '#facc15'
            if cell == world.start: color = '#22c55e'
            if cell == world.goal: color = '#ef4444'
            ax.add_patch(Rectangle((c, r), 1, 1, facecolor=color, edgecolor='#ffffff', linewidth=1))
    ax.text(world.start[1]+.5,world.start[0]+.5,'S',ha='center',va='center',fontweight='bold')
    ax.text(world.goal[1]+.5,world.goal[0]+.5,'G',ha='center',va='center',fontweight='bold')
    ax.set_xlim(0, world.cols); ax.set_ylim(world.rows, 0)
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(f'Dijkstra example: cost {result.cost:.0f} | {result.nodes_expanded} nodes expanded', fontsize=15)
    fig.tight_layout()
    fig.savefig(output, dpi=160, bbox_inches='tight')
    plt.close(fig)


if __name__ == '__main__':
    create_figure(str(Path(__file__).with_name('example_result.png')))
