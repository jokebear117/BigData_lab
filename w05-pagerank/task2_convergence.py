#!/usr/bin/env python3
"""Week 5 · Task 2 — How long does it take to converge, and on what?

Textbook §5.1, §5.2.

The textbook says PageRank converges. It does not say in how many iterations,
because the answer depends on beta, on the graph, and on what you are willing
to call "converged". Those three knobs are yours to turn, on your machine,
with a graph big enough that you can feel the cost.

    python3 task2_convergence.py --betas 0.5,0.7,0.85,0.95,0.99
    python3 task2_convergence.py --nodes 20000 --betas 0.85,0.95

Your timings are about your hardware. The iteration counts are not - those are
about the mathematics, and everybody should get the same ones.
"""
import argparse, json, os, platform, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def machine():
    processor = platform.processor() or platform.machine()
    try:
        with open("/proc/cpuinfo") as f:
            processor = next(line.split(":", 1)[1].strip() for line in f
                             if line.startswith("model name"))
    except (OSError, StopIteration):
        pass
    ram_gib = None
    try:
        with open("/proc/meminfo") as f:
            ram_gib = round(int(next(line.split()[1] for line in f
                                     if line.startswith("MemTotal:"))) / 1024**2, 1)
    except (OSError, StopIteration, ValueError):
        pass
    return {"platform": platform.platform(), "processor": processor,
            "ram_gib": ram_gib, "python": platform.python_version()}


def write_markdown(data):
    rows = sorted(data.get("runs", []), key=lambda r: (r["nodes"], r["tol"], r["beta"]))
    lines = ["# PageRank convergence measurements", "",
             f"Machine: {data['machine'].get('processor')} · "
             f"{data['machine'].get('ram_gib')} GiB RAM · "
             f"{data['machine'].get('platform')} · Python {data['machine'].get('python')}", "",
             "| Nodes | β | Tolerance | Iterations | Seconds | Top 10 |",
             "|---:|---:|---:|---:|---:|---|"]
    for r in rows:
        lines.append(f"| {r['nodes']:,} | {r['beta']:g} | {r['tol']:g} | "
                     f"{r['iterations']} | {r['seconds']:.3f} | "
                     f"{', '.join(r['top10'])} |")
    lines += ["", "See `observation.md` for interpretation of beta, graph size, "
              "tolerance, and top-10 changes.", ""]
    with open(os.path.join(OUT, "convergence.md"), "w") as f:
        f.write("\n".join(lines))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--betas", default="0.5,0.7,0.85,0.95,0.99")
    p.add_argument("--nodes", type=int, default=None,
                   help="graph size; default is the harness graph")
    p.add_argument("--tol", type=float, default=1e-10)
    a = p.parse_args()
    os.makedirs(OUT, exist_ok=True)

    import bench
    if a.nodes:
        bench.NODES = a.nodes
    graph = bench.build()

    from task1_pagerank import pagerank

    rows = []
    for beta in [float(x) for x in a.betas.split(",")]:
        t0 = time.perf_counter()
        ranks = pagerank(graph, beta=beta, iterations=500, tol=a.tol)
        elapsed = time.perf_counter() - t0
        iters = getattr(pagerank, "iterations", None)
        top = sorted(ranks.items(), key=lambda kv: -kv[1])[:10]
        rows.append({"beta": beta, "nodes": len(graph), "tol": a.tol,
                     "iterations": iters, "seconds": elapsed,
                     "top10": [k for k, _ in top]})
        print(f"  beta {beta:<5}  {str(iters):>4} iterations  {elapsed:>7.3f}s   "
              f"top: {', '.join(k for k, _ in top[:3])}")

    path = os.path.join(OUT, "convergence.json")
    prior = json.load(open(path)) if os.path.exists(path) else {"runs": []}
    prior["machine"] = machine()
    prior["runs"].extend(rows)
    with open(path, "w") as f:
        json.dump(prior, f, indent=2)
    write_markdown(prior)
    print(f"\n  -> out/convergence.json  ({len(prior['runs'])} run(s))")


if __name__ == "__main__":
    main()
