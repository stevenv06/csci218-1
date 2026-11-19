"""Compare the group's search implementations on paired grid layouts."""

import argparse
from collections import defaultdict, deque
from dataclasses import dataclass
from hashlib import sha256
import json
from math import inf, isfinite
from pathlib import Path
import platform
from random import Random
from statistics import mean, stdev
from time import get_clock_info

from astar import astar
from dijkstra import dijkstra
from grid import GridWorld


SIZES = [(20, 30), (40, 60), (80, 120)]
DENSITIES = [15, 30]
LAYOUTS_PER_DENSITY = 12
SEARCHES = {"dijkstra": dijkstra, "astar": astar}
ALGORITHMS = tuple(SEARCHES)


@dataclass
class Case:
    name: str
    kind: str
    world: GridWorld
    nominal_density_percent: int | None = None
    seed: int | None = None


def make_cases():
    cases = []
    for size_index, (rows, cols) in enumerate(SIZES):
        start, goal = (1, 1), (rows - 2, cols - 2)
        label = f"{rows}x{cols}"
        cases.append(Case(f"{label}-open", "open", GridWorld(rows, cols, start, goal), 0))

        available = [
            (r, c)
            for r in range(rows)
            for c in range(cols)
            if (r, c) not in (start, goal)
        ]
        for density in DENSITIES:
            obstacle_count = round(rows * cols * density / 100)
            for index in range(LAYOUTS_PER_DENSITY):
                seed = 218000 + 1000 * size_index + 20 * density + index
                obstacles = set(Random(seed).sample(available, obstacle_count))
                world = GridWorld(rows, cols, start, goal, obstacles)
                cases.append(Case(f"{label}-{density}pct-{index + 1:02}", "random", world, density, seed))

        partition = {(r, cols // 2) for r in range(rows)}
        cases.append(Case(f"{label}-partition", "partition", GridWorld(rows, cols, start, goal, partition)))

    Random(218).shuffle(cases)
    return cases


def reference_cost(world):
    """Compute the minimum number of unit-cost moves with breadth-first search."""
    queue = deque([(world.start, 0)])
    seen = {world.start}
    while queue:
        (row, col), distance = queue.popleft()
        if (row, col) == world.goal:
            return distance
        for neighbor in ((row - 1, col), (row, col + 1), (row + 1, col), (row, col - 1)):
            if neighbor not in seen and world.passable(neighbor):
                seen.add(neighbor)
                queue.append((neighbor, distance + 1))
    return None


def validate(case, algorithm, result, expected_cost):
    world = case.world
    ok = (
        isfinite(result.elapsed_ms)
        and result.elapsed_ms >= 0
        and result.nodes_expanded == len(result.explored_order) == len(set(result.explored_order))
        and result.explored_order[0] == world.start
        and result.found == (expected_cost is not None)
    )
    if expected_cost is None:
        ok = ok and result.cost == inf and result.path == []
    else:
        ok = (
            ok and result.cost == expected_cost == len(result.path) - 1
            and result.path[0] == world.start and result.path[-1] == world.goal
            and result.explored_order[-1] == world.goal
            and all(world.passable(cell) for cell in result.path)
            and all(abs(r1 - r2) + abs(c1 - c2) == 1
                    for (r1, c1), (r2, c2) in zip(result.path, result.path[1:]))
        )
    if not ok:
        raise RuntimeError(f"Validation failed for {algorithm} on {case.name}")


def prepare_case(case):
    world = case.world
    expected_cost = reference_cost(world)
    stats = {}
    for algorithm in ALGORITHMS:
        result = SEARCHES[algorithm](world)
        validate(case, algorithm, result, expected_cost)
        stats[algorithm] = {"nodes_expanded": result.nodes_expanded, "elapsed_ms": []}

    return {
        "layout": case.name,
        "kind": case.kind,
        "rows": world.rows,
        "cols": world.cols,
        "start": world.start,
        "goal": world.goal,
        "nominal_density_percent": case.nominal_density_percent,
        "seed": case.seed,
        "obstacle_count": len(world.obstacles),
        "obstacles": sorted(world.obstacles),
        "found": expected_cost is not None,
        "path_cost": expected_cost,
        "first_algorithm_by_trial": [],
        "algorithms": stats,
    }


def record_pair(case, layout, trial, layout_index):
    order = ALGORITHMS if (trial + layout_index) % 2 == 0 else ALGORITHMS[::-1]
    layout["first_algorithm_by_trial"].append(order[0])
    expected_cost = layout["path_cost"] if layout["found"] else inf
    results = {algorithm: SEARCHES[algorithm](case.world) for algorithm in order}
    for algorithm, result in results.items():
        stats = layout["algorithms"][algorithm]
        if (result.nodes_expanded != stats["nodes_expanded"]
                or result.found != layout["found"] or result.cost != expected_cost
                or not isfinite(result.elapsed_ms) or result.elapsed_ms < 0):
            raise RuntimeError(f"Inconsistent result for {algorithm} on {case.name}")
        stats["elapsed_ms"].append(result.elapsed_ms)


def summarize(layouts):
    groups = defaultdict(list)
    for layout in layouts:
        label = (
            layout["rows"], layout["cols"], layout["kind"],
            layout["nominal_density_percent"], layout["found"],
        )
        groups[label].append(layout)

    summary = []
    for (rows, cols, kind, density, found), cases in sorted(groups.items()):
        entry = {
            "rows": rows, "cols": cols, "kind": kind,
            "nominal_density_percent": density, "found": found,
            "layouts": len(cases),
            "mean_path_cost": mean(case["path_cost"] for case in cases) if found else None,
        }
        for algorithm in ALGORITHMS:
            times = [ms for case in cases for ms in case["algorithms"][algorithm]["elapsed_ms"]]
            entry[algorithm] = {
                "mean_ms": mean(times),
                "sample_sd_ms": stdev(times) if len(times) > 1 else None,
                "mean_nodes_expanded": mean(case["algorithms"][algorithm]["nodes_expanded"] for case in cases),
                "timed_runs": len(times),
            }
        summary.append(entry)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=24, help="Timed run pairs per layout, a positive even number")
    parser.add_argument("--output", type=Path, default=Path("benchmark_results.json"))
    args = parser.parse_args()
    if args.pairs <= 0 or args.pairs % 2:
        parser.error("--pairs must be a positive even number")

    cases = make_cases()
    layouts = [prepare_case(case) for case in cases]
    round_order = list(range(len(cases)))
    schedule_rng = Random(218)
    for trial in range(args.pairs):
        schedule_rng.shuffle(round_order)
        for index in round_order:
            record_pair(cases[index], layouts[index], trial, index)

    sources = ["grid.py", "dijkstra.py", "astar.py", "search_result.py"]
    base = Path(__file__).resolve().parent
    data = {
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "os": platform.platform(),
            "processor": platform.processor(),
            "perf_counter_resolution_seconds": get_clock_info("perf_counter").resolution,
        },
        "source_sha256": {name: sha256((base / name).read_bytes()).hexdigest() for name in sources},
        "warmup_runs_per_algorithm_per_layout": 1,
        "timed_run_pairs_per_layout": args.pairs,
        "timed_searches": len(layouts) * args.pairs * len(SEARCHES),
        "summary": summarize(layouts),
        "layouts": layouts,
    }
    args.output.write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Saved {data['timed_searches']:,} timed searches across {len(layouts)} layouts to {args.output}.")


if __name__ == "__main__":
    main()
