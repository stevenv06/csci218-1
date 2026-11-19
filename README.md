# CSCI218 Topic 8 — Intelligent Pathfinding Using Dijkstra and A* Search

An interactive Python/Pygame simulator that compares **Dijkstra's algorithm** and **A\* search** on a 4-directional, unit-cost grid. Both algorithms run on the same `GridWorld` and return the same `SearchResult`, so their path cost, nodes expanded and search time can be compared fairly.

## Requirements

- Python 3.10 or newer
- Pygame 2.5+ (only needed for the graphical app)

## Install and run

```bash
git clone <repository-url>
cd <repository-folder>
python -m pip install -r requirements.txt
python app.py
```

On Windows you can use `py -3 app.py`. On macOS/Linux, use `python3` if `python` is not found.

### Without Pygame (no window)

```bash
python demo_cli.py                 # Dijkstra on a small map, printed as text
python -m unittest discover -v     # run all 12 automated tests
```

## Controls

| Key / action | Effect |
|---|---|
| `1` + left click / drag | Draw or erase walls |
| `2` + left click | Move the start cell |
| `3` + left click | Move the goal cell |
| `4` | Select Dijkstra |
| `5` | Select A* |
| `SPACE` | Run the selected algorithm, animate explored cells, then show the final path |
| `R` | Generate reproducible random walls (seed 218) |
| `C` | Clear all walls |
| `ESC` | Quit |

Colours: green = start, red = goal, dark grey = wall, blue = explored, yellow = final path. The status bar shows path cost, nodes expanded and algorithm-only search time. Changing the map or the algorithm clears the previous result.

## Project structure

| File | Purpose | Member |
|---|---|---|
| `grid.py` | `GridWorld` model: bounds, walls, start/goal validation, `neighbors()` | 1 |
| `app.py` | Pygame interface, algorithm selection, search animation | 1 (A* switch by 3) |
| `dijkstra.py` | Dijkstra search and the shared `SearchResult` dataclass | 2 |
| `astar.py` | A* search with Manhattan-distance heuristic | 3 |
| `test_project.py` | 7 tests: grid rules and Dijkstra | 1, 2 |
| `test_astar.py` | 5 tests: A*, heuristic, agreement with Dijkstra | 3 |
| `demo_cli.py` | Non-graphical Dijkstra example | 1, 2 |
| `make_example_figure.py` | Generates `example_result.png` (needs matplotlib) | 1, 2 |
| `requirements.txt` | Python dependencies | 5 |

Member 4's benchmark code and results are in the experiments folder/notebook and the group report.

## Algorithm contract

Every algorithm has the signature `algorithm(world: GridWorld) -> SearchResult`.

- Moves come only from `world.neighbors(cell)`: up, down, left, right, each costing 1. No diagonals.
- `SearchResult` fields: `path`, `cost`, `explored_order`, `nodes_expanded`, `elapsed_ms`, `found`.
- If no route exists: `found=False`, `path=[]`, `cost=inf`.
- When a route exists, `cost == len(path) - 1`.
- A* uses Manhattan distance `|r - r_goal| + |c - c_goal|`, which is admissible and consistent for this grid.

## How results are measured

- `elapsed_ms` uses `time.perf_counter()` and covers search plus path reconstruction only; drawing and animation are excluded.
- `nodes_expanded` counts each cell once, when it is removed from the priority queue (including the goal, if reached).
- Benchmarks compare both algorithms on identical maps with fixed random seeds and repeated timed runs.

## Troubleshooting

- `Pygame is required for the UI`: run `python -m pip install -r requirements.txt`.
- Nothing happens on `SPACE`: make sure the window is focused; the start and goal cannot be walls.
- "No route exists": walls fully separate start from goal. Press `C` or move a wall.

## Git workflow

Each member commits their own work with a meaningful message, for example `Add reusable grid model`, `Implement Dijkstra search`, `Implement A* search`, `Add algorithm switching to UI`, `Add benchmark experiments`, `Add README and report`. Use `git log --author="<name>"` to check contribution history.
