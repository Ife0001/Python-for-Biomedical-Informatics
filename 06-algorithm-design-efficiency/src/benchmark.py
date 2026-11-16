"""Reproducible benchmark with CSV and simple SVG visualization; stdlib only."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import median
from time import perf_counter_ns

from algorithms import make_dataset, quicksort

KINDS = ("random", "sorted", "reversed", "identical")
METHODS = ("first_pivot", "random_pivot", "python_sorted")
FIELDS = ("dataset", "size", "method", "trials", "median_ms", "min_ms", "max_ms")


def run_benchmark(sizes: tuple[int, ...] = (100, 500, 1000), trials: int = 5, seed: int = 42):
    if not sizes or any(n < 0 for n in sizes) or trials < 1:
        raise ValueError("sizes must be nonnegative and trials >= 1")
    rows = []
    for size in sizes:
        for kind in KINDS:
            baseline = make_dataset(kind, size, seed=seed + size)
            expected = sorted(baseline)
            for method in METHODS:
                times = []
                for trial in range(trials):
                    data = baseline.copy()  # cloning deliberately excluded from timing
                    start = perf_counter_ns()
                    if method == "python_sorted":
                        result = sorted(data)
                    else:
                        quicksort(data, pivot="first" if method == "first_pivot" else "random", seed=seed + trial)
                        result = data
                    elapsed = (perf_counter_ns() - start) / 1_000_000
                    if result != expected:
                        raise AssertionError(f"incorrect sorting: {kind}/{size}/{method}")
                    times.append(elapsed)
                rows.append({"dataset": kind, "size": size, "method": method,
                             "trials": trials, "median_ms": round(median(times), 6),
                             "min_ms": round(min(times), 6), "max_ms": round(max(times), 6)})
    return rows


def write_svg(rows: list[dict], dest: Path):
    """Simple benchmark chart for the largest size of random-input arrays."""
    selected_size = max(row["size"] for row in rows)
    subset = [r for r in rows if r["size"] == selected_size and r["dataset"] == "random"]
    longest = max((r["median_ms"] for r in subset), default=1) or 1
    import html
    width = 790
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 300">',
             '<rect width="100%" height="100%" fill="white"/>',
             f'<text x="25" y="32" font-family="Arial" font-size="18" fill="#17202a">Sorting times: random array, n={selected_size}</text>',
             '<text x="25" y="57" font-family="Arial" font-size="12" fill="#555">Median milliseconds; lower is faster; illustrative local machine results</text>']
    colors = ("#2874a6", "#168d76", "#a15c23")
    for idx, r in enumerate(subset):
        y = 85 + idx * 65
        length = 440 * r["median_ms"] / longest
        lines.extend([f'<text x="25" y="{y+18}" font-family="Arial" font-size="14" fill="#222">{html.escape(r["method"])}</text>',
                      f'<rect x="180" y="{y}" width="{length:.1f}" height="27" fill="{colors[idx]}" rx="3"/>',
                      f'<text x="{190+length:.1f}" y="{y+19}" font-family="Arial" font-size="13" fill="#333">{r["median_ms"]:.4f} ms</text>'])
    lines.append('</svg>')
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text('\n'.join(lines), encoding="utf-8")


def main():
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", nargs="+", type=int, default=[100, 500, 1000])
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    rows = run_benchmark(tuple(args.sizes), args.trials, args.seed)
    output = root / "outputs"
    output.mkdir(exist_ok=True)
    with (output / "sorting_benchmarks.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    report = {"dataset_types": list(KINDS), "methods": list(METHODS), "sizes": args.sizes,
              "trials_per_combination": args.trials, "comparisons": len(rows),
              "all_sorted_outputs_verified": True,
              "caveat": "Timings depend on hardware and Python runtime; this is not a clinical performance benchmark."}
    (output / "benchmark_metadata.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    write_svg(rows, root / "figures" / "random_array_sorting.svg")
    print(json.dumps(report, indent=2))
    print("Saved outputs/sorting_benchmarks.csv, outputs/benchmark_metadata.json, figures/random_array_sorting.svg")


if __name__ == "__main__":
    main()
