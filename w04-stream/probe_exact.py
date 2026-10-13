#!/usr/bin/env python3
"""Probe exact-set burden in a fresh process; emit actual measurements as JSON.

Usage: python3 probe_exact.py TARGET_N
Stop at 30 seconds or peak RSS >= 25% of WSL RAM, checking every 100,000 items.
A stopped prefix is explicitly distinguished from a completed target stream.
This Linux-only helper includes tracemalloc overhead in process RSS.
"""
import json, os, random, resource, sys, time, tracemalloc
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from task2_limits import stream
n = int(sys.argv[1])
with open('/proc/meminfo') as f:
    total_ram = next(int(line.split()[1]) * 1024 for line in f if line.startswith('MemTotal:'))
rss_limit = total_ram // 4
tracemalloc.start()
t0 = time.perf_counter()
seen = set()
reason = None
for consumed, item in enumerate(stream(n), 1):
    seen.add(item)
    if consumed % 100_000 == 0:
        elapsed = time.perf_counter() - t0
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        if rss >= rss_limit:
            reason = 'Measured process peak RSS reached 25% of WSL RAM; stopped before exhaustion.'
        elif elapsed >= 30:
            reason = 'Exact processing exceeded 30 seconds; stopped at the predeclared interactive latency threshold.'
        if reason:
            break
elapsed = time.perf_counter() - t0
peak = tracemalloc.get_traced_memory()[1]
tracemalloc.stop()
row = dict(target_n=n, consumed=consumed, completed=consumed==n,
           observed_distinct=len(seen), exact_s=elapsed, exact_peak_bytes=peak,
           process_peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
           rss_threshold_bytes=rss_limit, time_threshold_s=30,
           stopped_reason=reason)
print(json.dumps(row), flush=True)
