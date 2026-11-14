# CSCI218 Topic 8 — Member 1 + Member 2 Deliverables

**Topic:** Intelligent Pathfinding Using Dijkstra and A* Search  
**Included scope:** Member 1 (grid world, Pygame interface) and Member 2 (Dijkstra algorithm).  
**Not included:** Member 3's A* implementation, Member 4's experimental comparison, or the group-wide final report. These must be integrated by the team.

## Quick start

Requires Python 3.10+.

```bash
python -m pip install -r requirements.txt
python app.py
```

To run the algorithm without installing Pygame:

```bash
python demo_cli.py
python -m unittest discover -v
```

## Controls

| Key / action | Effect |
|---|---|
| `1` + left click / drag | Draw or erase obstacles |
| `2` + left click | Move starting cell |
| `3` + left click | Move goal cell |
| `SPACE` | Run Dijkstra and animate explored cells, then final path |
| `R` | Generate reproducible random obstacles (seed 218) |
| `C` | Clear obstacles |
| `ESC` | Exit |

## Project structure

- `grid.py`: self-contained, reusable GridWorld model and validation (Member 1).
- `app.py`: Pygame simulation, interaction and step-by-step search animation (Member 1).
- `dijkstra.py`: Dijkstra's shortest-path algorithm and metrics (Member 2).
- `demo_cli.py`: non-graphical reproducible usage example.
- `test_project.py`: model, boundary, path validity and no-route tests.
- `example_result.png`: visual output generated from the real algorithm by `make_example_figure.py`.
- `make_example_figure.py`: create example figure (matplotlib required for this optional script).
- `Member_1_2_Report_Sections.docx`: report draft, with integration placeholders.

## Algorithm contract for Member 3 (A*)

Both algorithms must be called on the **same** `GridWorld` instance, with `world.neighbors(cell)` and a unit cost per legal orthogonal move; no diagonal moves. Implement `astar(world: GridWorld) -> SearchResult` in `astar.py` and return `SearchResult` from `dijkstra.py` (path, cost, explored_order, nodes_expanded, elapsed_ms, found).

For a four-direction unit-cost grid, use Manhattan distance `abs(r-r_goal)+abs(c-c_goal)` for A*. It is admissible and consistent. Member 3 should write `astar.py` and share it with the group. Do not claim the full group A* comparison is complete until it is implemented and tested.

## Notes on measurement

`elapsed_ms` is **algorithm-only time** measured using `time.perf_counter()`: it excludes Pygame animation/drawing. `nodes_expanded` counts unique settled cells removed from the frontier, including the goal when reached. Path cost counts grid edges (one per move), so `cost == len(path) - 1` when a path exists. No route yields `found=False`, `path=[]`, `cost=inf`.

For Member 4: compare both algorithms on identical world instances, several grid sizes/obstacle densities and fixed random seeds, using repeated runs with reported average and standard deviation.

## Git contribution evidence

Commit  files to the shared Git repository, with meaningful commit messages, e.g. `Add reusable grid model`, `Implement Dijkstra search`, `Add Pygame interaction`, `Add validation tests`. . 
