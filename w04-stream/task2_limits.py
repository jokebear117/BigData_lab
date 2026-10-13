#!/usr/bin/env python3
"""Week 4 · Task 2 — Find the size where exact stops being possible.

Textbook §4.1 (the stream model), §4.4, §4.5.

Sketches exist because the exact answer does not fit. That sentence is easy to
agree with and hard to feel, so this task makes you watch it happen on your own
machine: hold every distinct item in a set, keep raising the stream size, and
record where your laptop stops coping.

    python3 task2_limits.py --sizes 100000,400000,1600000
    python3 task2_limits.py --sizes 6400000            # keep going

Your numbers will not match anybody else's. That is the point.
"""
import argparse, json, os, platform, time, tracemalloc


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def machine(other_running="not recorded"):
    info = {"platform": platform.platform(),
            "processor": platform.processor() or platform.machine(),
            "python": platform.python_version(),
            "other_running": other_running}
    # Linux reports the CPU model and host RAM; containers may have less RAM.
    if os.path.exists("/proc/cpuinfo"):
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    info["processor"] = line.split(":", 1)[1].strip()
                    break
    if os.path.exists("/proc/meminfo"):
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    info["ram_bytes"] = int(line.split()[1]) * 1024
                    break
    return info


def write_report(data):
    """Write measured results; the user supplies the actual stopping reason."""
    info = data["machine"]
    lines = ["# Task 2 measurements", "",
             f"- Platform: {info['platform']}",
             f"- CPU: {info['processor']}",
             f"- Python: {info['python']}",
             f"- Host RAM: {info.get('ram_bytes', 'not recorded')} bytes",
             f"- Other running work: {info['other_running']}",
             f"- Stopping reason (A2): {data.get('stop_reason', 'Not recorded; these measurements do not establish a limit.')}",
             "", "Memory is tracemalloc peak Python allocation, not total process RSS.",
             "Container memory limits may differ from host RAM.", "",
             "| n | distinct | exact seconds | exact peak bytes | FM seconds | FM peak bytes | FM / truth |",
             "|---:|---:|---:|---:|---:|---:|---:|"]
    for row in data["runs"]:
        lines.append(f"| {row['n']} | {row['true_distinct']} | {row['exact_s']:.3f} | "
                     f"{row['exact_peak_bytes']} | {row.get('fm_s', 0):.3f} | "
                     f"{row.get('fm_peak_bytes', 'N/A')} | {row.get('fm_ratio', 0):.3f} |")
    stress = data.get("exact_stress_runs", [])
    if stress:
        lines.extend(["", "## Additional exact-only stress measurements", "",
                      "Both methods were compared in the table above. The following runs only probe exact-set burden.",
                      "Predeclared stopping criteria: 30 seconds or process RSS >= 25% of WSL RAM.",
                      "Stopped runs count only consumed items; they are not completed measurements of target n.", "",
                      "| target n | consumed | completed | distinct in consumed prefix | exact seconds | Python peak bytes | process peak RSS bytes |",
                      "|---:|---:|:---:|---:|---:|---:|---:|"])
        for row in stress:
            lines.append(f"| {row['target_n']} | {row['consumed']} | {row['completed']} | "
                         f"{row['observed_distinct']} | {row['exact_s']:.3f} | "
                         f"{row['exact_peak_bytes']} | {row['process_peak_rss_bytes']} |")
        lines.extend(["", "RSS includes interpreter and tracemalloc bookkeeping, beyond the set's Python allocations.",
                      "Each stress size runs in a fresh Python process."])
    # Use the latest run per size when comparing the endpoints.
    rows = sorted({r["n"]: r for r in data["runs"]}.values(), key=lambda r: r["n"])
    if len(rows) >= 2:
        import math
        first, last = rows[0], rows[-1]
        span = last["n"] / first["n"]
        lines.extend(["", f"Endpoint comparison: n increased {span:.1f}x."])
        for name, key in [("Exact", "exact_peak_bytes"), ("FM", "fm_peak_bytes")]:
            if first.get(key, 0) and last.get(key, 0):
                factor = last[key] / first[key]
                exponent = math.log(factor) / math.log(span)
                lines.append(f"- {name}: memory increased {factor:.2f}x; empirical exponent {exponent:.2f} (memory ~ n^exponent).")
    lines.extend(["", "Expected growth: exact O(distinct), FM O(n_hashes) for fixed 64-bit hashes.",
                  "FM accuracy ratios above show estimation error at each size; error need not decrease with n."])
    with open(os.path.join(OUT, "limits.md"), "w") as f:
        f.write("\n".join(lines) + "\n")


def stream(n, distinct_ratio=0.4, seed=246):
    """A stream of n items with about n*distinct_ratio distinct values."""
    import random
    rng = random.Random(seed)
    span = max(1, int(n * distinct_ratio))
    for _ in range(n):
        yield f"key-{rng.randrange(span)}"


def exact_distinct(n):
    """The honest answer: hold every distinct item."""
    tracemalloc.start()
    t0 = time.perf_counter()
    seen = set()
    for x in stream(n):
        seen.add(x)
    elapsed = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return len(seen), elapsed, peak


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sizes", default="100000,400000,1600000")
    p.add_argument("--other-running", default="not recorded",
                   help="describe other work running during the measurement")
    p.add_argument("--stop-reason", help="size where exact became unpleasant, and why")
    a = p.parse_args()
    sizes = [int(x) for x in a.sizes.split(",")]
    if any(n <= 0 for n in sizes):
        p.error("sizes must be positive")
    os.makedirs(OUT, exist_ok=True)

    try:
        from task1_sketches import flajolet_martin
    except Exception:
        flajolet_martin = None

    rows = []
    for n in sizes:
        true, t_exact, m_exact = exact_distinct(n)
        row = {"n": n, "true_distinct": true, "exact_s": t_exact,
               "exact_peak_bytes": m_exact}

        if flajolet_martin is not None:
            try:
                tracemalloc.start()
                t0 = time.perf_counter()
                est = flajolet_martin(stream(n))
                t_fm = time.perf_counter() - t0
                _, m_fm = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                row.update({"fm_estimate": est, "fm_s": t_fm,
                            "fm_peak_bytes": m_fm,
                            "fm_ratio": est / true if true else None})
            except NotImplementedError:
                tracemalloc.stop()

        rows.append(row)
        line = (f"  n={n:>10,}  distinct {true:>9,}   exact {t_exact:>7.2f}s "
                f"{m_exact / 1e6:>8.1f} MB")
        if "fm_s" in row:
            line += (f"   |  fm {row['fm_s']:>7.2f}s {row['fm_peak_bytes'] / 1e6:>6.2f} MB"
                     f"  {row['fm_ratio']:.2f}x")
        print(line)

    path = os.path.join(OUT, "limits.json")
    prior = json.load(open(path)) if os.path.exists(path) else {"runs": []}
    prior["machine"] = machine(a.other_running)
    if a.stop_reason:
        prior["stop_reason"] = a.stop_reason
    prior["runs"].extend(rows)
    with open(path, "w") as f:
        json.dump(prior, f, indent=2)
    write_report(prior)
    print(f"\n  -> out/limits.json  ({len(prior['runs'])} measurement(s))")
    print("  Keep raising --sizes until the exact version is unbearable. "
          "Record where, and what ran out.")


if __name__ == "__main__":
    main()
