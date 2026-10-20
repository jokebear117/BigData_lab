# Task 2 · Support and pair-counter growth

`task2_explosion.py` ran on 20,000 generated baskets (2,000-item universe) in WSL2, Python 3.12.3. The host reported in the existing w04 observation is a Galaxy Book5 Pro, Core Ultra 5 226V, 16 GB RAM; VS Code and ChatGPT/Codex were open.

| Support | Frequent pairs | Peak pair counters | Peak traced memory | Time |
|---:|---:|---:|---:|---:|
| 400 | 249 | 10,585 | 1.1 MB | 0.78 s |
| 200 | 776 | 58,626 | 6.4 MB | 1.51 s |
| 100 | 2,244 | 273,701 | 26.5 MB | 2.63 s |
| 50 | 6,397 | 820,259 | 102.4 MB | 3.93 s |
| 25 | 17,045 | 893,456 | 102.4 MB | 4.65 s |
| 12 | 43,116 | 893,456 | 102.7 MB | 4.77 s |
| 6 | 101,938 | 893,456 | 119.5 MB | 5.14 s |
| 3 | 250,054 | 893,456 | 156.6 MB | 5.09 s |
| 1 | 893,456 | 893,456 | 327.1 MB | 7.05 s |

```text
Peak pair counters (thousands), by support: 400 █  200 ███  100 ███████████  50 ██████████████████████████████  25–1 ████████████████████████████████
Frequent pairs (thousands), by support:     400 ▏  200 ▏    100 ▏          50 ▏                         25 ▋ 12 ███ 6 ███████ 3 █████████████████ 1 ████████████████████████████████
```

Halving support caused counters to grow by 5.54×, 4.67×, then 3.00× from 400 down to 50; after 25 they plateaued at 893,456 because that is the number of distinct pairs observed in these baskets. The answer count instead rose from 6,397 at support 50 to 893,456 at support 1. The gap means a modest threshold reduction can create a huge counting workload even while the useful answers remain much fewer.

Support 1 was the practical stopping point: traced peak memory reached 327 MB and took 7.05 s, but neither time nor memory actually failed on this 16 GB host. The generated data itself capped the counters; this experiment did not exhaust the machine.
