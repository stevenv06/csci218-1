"""Member 1: reusable grid-world model, independent of rendering and algorithms."""
from dataclasses import dataclass, field
from typing import Iterable

Cell = tuple[int, int]  # (row, column)


@dataclass
class GridWorld:
    rows: int = 20
    cols: int = 30
    start: Cell = (2, 2)
    goal: Cell = (17, 27)
    obstacles: set[Cell] = field(default_factory=set)

    def __post_init__(self) -> None:
        if self.rows < 2 or self.cols < 2:
            raise ValueError('Grid dimensions must both be at least 2')
        if not self.in_bounds(self.start) or not self.in_bounds(self.goal):
            raise ValueError('Start and goal must be inside the grid')
        if self.start == self.goal:
            raise ValueError('Start and goal must be different')
        if any(not self.in_bounds(cell) for cell in self.obstacles):
            raise ValueError('Obstacles must be inside the grid')
        if self.start in self.obstacles or self.goal in self.obstacles:
            raise ValueError('Start and goal cannot be blocked')

    def in_bounds(self, cell: Cell) -> bool:
        r, c = cell
        return 0 <= r < self.rows and 0 <= c < self.cols

    def passable(self, cell: Cell) -> bool:
        return self.in_bounds(cell) and cell not in self.obstacles

    def neighbors(self, cell: Cell) -> Iterable[Cell]:
        """Valid orthogonal moves; each move costs exactly one."""
        r, c = cell
        for candidate in ((r - 1, c), (r, c + 1), (r + 1, c), (r, c - 1)):
            if self.passable(candidate):
                yield candidate

    def toggle_obstacle(self, cell: Cell) -> bool:
        """Toggle a wall. Return whether a change occurred."""
        if not self.in_bounds(cell) or cell in (self.start, self.goal):
            return False
        if cell in self.obstacles:
            self.obstacles.remove(cell)
        else:
            self.obstacles.add(cell)
        return True

    def set_start(self, cell: Cell) -> bool:
        if not self.passable(cell) or cell == self.goal:
            return False
        self.start = cell
        return True

    def set_goal(self, cell: Cell) -> bool:
        if not self.passable(cell) or cell == self.start:
            return False
        self.goal = cell
        return True

    def clear_walls(self) -> None:
        self.obstacles.clear()
