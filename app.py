"""Member 1: interactive Pygame UI visualizing Member 2's Dijkstra search.

Run: python app.py. All search calculation happens separately from animation.
"""
import random
import sys
from grid import GridWorld
from dijkstra import SearchResult, dijkstra

try:
    import pygame
except ImportError:
    raise SystemExit('Pygame is required for the UI. Run: pip install -r requirements.txt')

CELL = 26
TOP = 116
BOTTOM = 46
FPS = 60
COLORS = {
    'bg': (15, 23, 42), 'panel': (30, 41, 59), 'empty': (241, 245, 249),
    'wall': (51, 65, 85), 'grid': (203, 213, 225), 'visited': (147, 197, 253),
    'path': (250, 204, 21), 'start': (34, 197, 94), 'goal': (239, 68, 68),
    'white': (248, 250, 252), 'muted': (203, 213, 225)
}


def run() -> None:
    pygame.init()
    world = GridWorld()
    width, height = world.cols * CELL, TOP + world.rows * CELL + BOTTOM
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('CSCI218 | Dijkstra Grid Pathfinding — Members 1 & 2')
    heading = pygame.font.SysFont('arial', 24, bold=True)
    regular = pygame.font.SysFont('arial', 16)
    small = pygame.font.SysFont('arial', 14)
    clock = pygame.time.Clock()
    result: SearchResult | None = None
    shown_explored = 0
    playback = False
    mode = 'wall'
    held_draw: bool | None = None

    def invalidate() -> None:
        nonlocal result, shown_explored, playback
        result, shown_explored, playback = None, 0, False

    def cell_from_mouse(pos: tuple[int, int]):
        x, y = pos
        row, col = (y - TOP) // CELL, x // CELL
        if y < TOP or not world.in_bounds((row, col)):
            return None
        return row, col

    def click_cell(cell, drag=False):
        nonlocal held_draw
        if cell is None:
            return
        if mode == 'start':
            if not drag and world.set_start(cell):
                invalidate()
        elif mode == 'goal':
            if not drag and world.set_goal(cell):
                invalidate()
        else:
            if drag:
                if cell not in (world.start, world.goal):
                    should_add = bool(held_draw)
                    if should_add and cell not in world.obstacles:
                        world.obstacles.add(cell)
                        invalidate()
                    elif not should_add and cell in world.obstacles:
                        world.obstacles.remove(cell)
                        invalidate()
            elif cell not in (world.start, world.goal):
                held_draw = cell not in world.obstacles
                if world.toggle_obstacle(cell):
                    invalidate()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click_cell(cell_from_mouse(event.pos))
            elif event.type == pygame.MOUSEMOTION and event.buttons[0] and mode == 'wall':
                click_cell(cell_from_mouse(event.pos), drag=True)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                held_draw = None
            elif event.type == pygame.KEYDOWN:
                key = event.key
                if key == pygame.K_1:
                    mode = 'wall'
                elif key == pygame.K_2:
                    mode = 'start'
                elif key == pygame.K_3:
                    mode = 'goal'
                elif key == pygame.K_SPACE:
                    result = dijkstra(world)
                    shown_explored = 0
                    playback = True
                elif key == pygame.K_c:
                    world.clear_walls()
                    invalidate()
                elif key == pygame.K_r:
                    rng = random.Random(218)
                    world.obstacles = {
                        (r, c) for r in range(world.rows) for c in range(world.cols)
                        if (r, c) not in (world.start, world.goal) and rng.random() < 0.24
                    }
                    invalidate()
                elif key == pygame.K_ESCAPE:
                    running = False

        if result is not None and playback:
            shown_explored = min(len(result.explored_order), shown_explored + 6)
            if shown_explored == len(result.explored_order):
                playback = False

        screen.fill(COLORS['bg'])
        screen.blit(heading.render('Dijkstra Pathfinding Visualizer', True, COLORS['white']), (16, 13))
        screen.blit(regular.render('1 Walls    2 Start    3 Goal    SPACE Search    R Random    C Clear    ESC Quit', True, COLORS['muted']), (16, 48))
        screen.blit(regular.render(f'Edit mode: {mode.upper()}     |     Left-click or drag walls', True, COLORS['white']), (16, 76))
        explored = set(result.explored_order[:shown_explored]) if result else set()
        path = set(result.path) if result and not playback else set()
        for r in range(world.rows):
            for c in range(world.cols):
                cell = (r, c)
                color = COLORS['empty']
                if cell in world.obstacles: color = COLORS['wall']
                elif cell in explored: color = COLORS['visited']
                if cell in path: color = COLORS['path']
                if cell == world.start: color = COLORS['start']
                if cell == world.goal: color = COLORS['goal']
                pygame.draw.rect(screen, color, (c * CELL + 1, TOP + r * CELL + 1, CELL - 2, CELL - 2), border_radius=2)

        if result:
            outcome = f'Path cost: {result.cost:.0f}' if result.found else 'No route exists'
            status = f'{outcome}    |    Expanded: {result.nodes_expanded}    |    Search: {result.elapsed_ms:.3f} ms'
            if playback: status = 'Visualizing explored nodes...    |    ' + status
        else:
            status = 'Set obstacles, then press SPACE to find a shortest route.'
        screen.blit(small.render(status, True, COLORS['white']), (14, height - 30))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit(0)


if __name__ == '__main__':
    run()
