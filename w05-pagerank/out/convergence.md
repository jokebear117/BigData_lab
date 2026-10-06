# Convergence observations

- Platform: Windows 11 x64, Intel Core Ultra 5 226V, 15.54 GiB RAM, Python 3.12.10. Browser, editor and ordinary desktop applications were open; no controlled isolation was used.
- For the 1,200-node graph at tolerance `1e-10`, iterations rose as beta approached 1, from 14 at 0.5 to 24 at 0.99. Larger beta means less teleportation and slower mixing; this graph has a small trap that retains probability for longer.

## Beta curve (1,200 nodes)

| beta | iterations | seconds |
|---:|---:|---:|
| 0.50 | 14 | 0.0057 |
| 0.70 | 17 | 0.0068 |
| 0.85 | 20 | 0.0082 |
| 0.95 | 23 | 0.0096 |
| 0.99 | 24 | 0.0096 |

## Graph size (beta 0.85, tolerance 1e-10)

| nodes | iterations | seconds |
|---:|---:|---:|
| 1,200 | 20 | 0.0082 |
| 20,000 | 21 | 0.1733 |

Iterations were nearly constant (20–21), while wall time rose about 21× as node count grew 16.7×: each iteration visits nodes and edges, while convergence depends mainly on beta, graph structure and tolerance.

## Tolerance and ranking

At 1,200 nodes and beta 0.85, tolerance `1e-6` took 12 iterations; `1e-10` took 20. Four extra decimal orders cost 8 iterations here. The ordered top 10 first changed at beta 0.7: p00004 moved ahead of p00000 (the top-10 membership remained the same through 0.99). For this graph the leading set is stable, but close positions can swap with beta, so a published rank should state its beta and graph.
