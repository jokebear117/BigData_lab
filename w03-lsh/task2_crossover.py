#!/usr/bin/env python3
"""Week 3 · Task 2 — Find the crossover on your own machine.

Run at least five sizes spanning 16x or more, then keep increasing --sizes
until the measurements become unpleasant. Results are appended to out/ and
out/curve.md is regenerated from all recorded runs.
"""
import argparse
import json
import os
import platform
import random
import time
import tracemalloc

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def machine():
    total_ram = None
    cpu = platform.processor() or platform.machine()
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as f:
            cpu = next(line.split(":", 1)[1].strip() for line in f
                       if line.lower().startswith("model name"))
    except (OSError, StopIteration):
        pass
    try:
        with open("/proc/meminfo", encoding="utf-8") as f:
            total_ram = int(next(line.split()[1] for line in f
                                 if line.startswith("MemTotal:"))) * 1024
    except (OSError, StopIteration, ValueError):
        pass
    if total_ram is None and hasattr(os, "sysconf"):
        try:
            total_ram = (os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES"))
        except (ValueError, OSError):
            pass
    return {
        "platform": platform.platform(),
        "processor": cpu,
        "other_workloads": "WSL active; user reports it uses a substantial share of RAM",
        "python": platform.python_version(),
        "ram_bytes": total_ram,
    }


def timed(fn, *args):
    """Return a call's result, wall time, and peak traced memory."""
    tracemalloc.start()
    try:
        t0 = time.perf_counter()
        result = fn(*args)
        elapsed = time.perf_counter() - t0
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return result, elapsed, peak


def write_curve(path, data):
    """Write a compact table and the requested quadratic/crossover checks."""
    # If a size was measured more than once, use its latest run in the curve.
    by_size = {row["n"]: row for row in data.get("runs", [])}
    runs = [by_size[n] for n in sorted(by_size)]
    lines = [
        "# Crossover measurements", "",
        f"- Platform: {data['machine'].get('platform', 'unknown')}",
        f"- CPU: {data['machine'].get('processor', 'unknown')}",
        f"- RAM: {data['machine'].get('ram_bytes') or 'unknown'} bytes",
        f"- Python: {data['machine'].get('python', 'unknown')}",
        f"- Other workloads running: {data['machine'].get('other_workloads', 'not recorded')}", "",
        "| n | brute (s) | brute comparisons | brute peak (MiB) | LSH (s) | LSH comparisons | LSH peak (MiB) |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in runs:
        mib = 1024 * 1024
        lines.append(
            f"| {row['n']} | {row['brute_s']:.4f} | {row['brute_calls']} "
            f"| {row['brute_peak_bytes'] / mib:.2f} "
            f"| {row.get('lsh_s', 0):.4f} | {row.get('lsh_calls', '—')} "
            f"| {row.get('lsh_peak_bytes', 0) / mib:.2f} |"
        )

    lines += ["", "## Brute-force doubling check", ""]
    doubled = []
    for left, right in zip(runs, runs[1:]):
        if right["n"] == 2 * left["n"] and left["brute_s"] > 0:
            ratio = right["brute_s"] / left["brute_s"]
            doubled.append((left["n"], right["n"], ratio))
            lines.append(f"- n={left['n']} → {right['n']}: time ratio {ratio:.2f}x (quadratic expectation: ~4x).")
    if not doubled:
        lines.append("- No adjacent measurements double n; add matching sizes to check the expected ~4x ratio.")
    else:
        ratios = [ratio for _, _, ratio in doubled]
        low, high = min(ratios), max(ratios)
        verdict = "consistent with roughly quadratic growth" if all(3 <= r <= 5 for r in ratios) else "not uniformly close to quadratic growth"
        lines.append(f"- Observed doubling ratios ranged from {low:.2f}x to {high:.2f}x; this is {verdict}.")

    slow = next((row for row in runs
                 if row["brute_s"] >= 60 or row.get("lsh_s", 0) >= 60), None)
    lines += ["", "## Unpleasant size and memory scope", ""]
    if slow:
        method = " and ".join(name for name, key in (("brute force", "brute_s"), ("LSH", "lsh_s"))
                              if slow.get(key, 0) >= 60)
        lines.append(f"- First measured size taking at least 60 seconds: n={slow['n']} ({method}).")
    else:
        lines.append("- No measured call took 60 seconds; continue with larger sizes to find the limit.")
    lines.append("- Peak memory below is additional memory tracked during find(); the input documents were built before tracing and are excluded.")

    crossing = next((r for r in runs if "lsh_s" in r and r["lsh_s"] < r["brute_s"]), None)
    lines += ["", "## Crossover and largest measurement", ""]
    if crossing:
        slower = max((r for r in runs if r["n"] < crossing["n"]), key=lambda r: r["n"], default=None)
        if slower:
            lines.append(f"- Brute force is faster through n={slower['n']}; LSH first wins at n={crossing['n']}.")
        else:
            lines.append(f"- First measured size where LSH is faster: n={crossing['n']}.")
    else:
        lines.append("- No measured size has LSH faster than brute force yet.")
    if runs:
        largest = max(runs, key=lambda row: row["n"])
        lines.append(f"- Largest n={largest['n']}: brute peak {largest['brute_peak_bytes'] / (1024**2):.2f} MiB; "
                     f"LSH peak {largest.get('lsh_peak_bytes', 0) / (1024**2):.2f} MiB.")
    lines += ["", "At small n, brute force wins because it avoids the per-document signature and band-hashing setup. Here LSH computes 120 hash minima for each of 60 shingles per document, then builds 30 band buckets; that linear setup is expensive until pair comparisons dominate.", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", default="250,500,1000,2000,4000",
                        help="comma-separated document counts; default spans 16x")
    parser.add_argument("--threshold", type=float, default=0.6)
    args = parser.parse_args()
    sizes = [int(value.strip()) for value in args.sizes.split(",") if value.strip()]
    if not sizes or any(n < 1 for n in sizes):
        parser.error("--sizes must contain positive document counts")
    os.makedirs(OUT, exist_ok=True)

    import bench
    from task3_scale import BruteForce, YourFinder

    def documents(n):
        # bench.build() caps at 2,120 docs. Extend deterministically so n is real.
        docs = bench.build()
        if n <= len(docs):
            return docs[:n]
        rng = random.Random(20261006)
        docs.extend(set(rng.sample(range(bench.VOCAB), bench.SHINGLES))
                    for _ in range(n - len(docs)))
        return docs[:n]

    rows = []
    for n in sizes:
        docs = documents(n)
        sim = bench.Counter()
        _, brute_s, brute_peak = timed(BruteForce(args.threshold).find, docs, sim)
        row = {"n": n, "brute_s": brute_s, "brute_calls": sim.calls,
               "brute_peak_bytes": brute_peak}

        sim_lsh = bench.Counter()
        _, lsh_s, lsh_peak = timed(YourFinder(args.threshold).find, docs, sim_lsh)
        row.update({"lsh_s": lsh_s, "lsh_calls": sim_lsh.calls,
                    "lsh_peak_bytes": lsh_peak})
        rows.append(row)
        print(f"  n={n:>6}  brute {brute_s:>8.2f}s {sim.calls:>12,} cmp  "
              f"|  lsh {lsh_s:>7.2f}s {sim_lsh.calls:>9,} cmp")

    result_path = os.path.join(OUT, "crossover.json")
    if os.path.exists(result_path):
        with open(result_path, encoding="utf-8") as f:
            prior = json.load(f)
    else:
        prior = {"runs": []}
    prior["machine"] = machine()
    prior["runs"].extend(rows)
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(prior, f, indent=2)
    curve_path = os.path.join(OUT, "curve.md")
    write_curve(curve_path, prior)
    print(f"\n  -> out/crossover.json ({len(prior['runs'])} measurements)")
    print("  -> out/curve.md")
    print("  Keep raising --sizes until something becomes unpleasant; record why in curve.md.")


if __name__ == "__main__":
    main()
