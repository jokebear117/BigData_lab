# Task 2 · Distance contrast across dimensions

20,000 random point pairs per run (1,000 generated points except where shown), WSL2 / Python 3.12.3. The host details recorded in w04 are Galaxy Book5 Pro, Core Ultra 5 226V, 16 GB RAM; VS Code and ChatGPT/Codex were open. The largest run, 200 dimensions, took 0.44 s.

| Dimensions | Mean distance | Contrast `(max−min)/min` | Relative SD |
|---:|---:|---:|---:|
| 2 | 0.521 | 488.582 | 0.476 |
| 5 | 0.884 | 14.257 | 0.282 |
| 10 | 1.274 | 3.925 | 0.193 |
| 20 | 1.815 | 2.253 | 0.135 |
| 50 | 2.867 | 0.982 | 0.083 |
| 100 | 4.068 | 0.545 | 0.060 |
| 200 | 5.776 | 0.372 | 0.041 |

Contrast fell below 1 at 50 dimensions and below 0.5 by 200 dimensions (it was 0.545 at 100). Mean distance grows approximately with the square root of dimension: mean/√d stays around 0.37–0.41 across the measurements, rather than growing linearly.

At dimension 50, changing point count from 500 to 1,000 to 2,000 produced contrasts 0.928, 0.982 and 1.022. The effect is modest here but present: more sampled points create more chances for an unusually close or far pair, so contrast depends on n as well as d. Relative standard deviation better describes concentration of typical distances; max/min contrast is more sensitive to sample extremes.

This result does not directly invalidate week 3 LSH: these measurements use Euclidean distance on uniform cube points, while LSH was evaluated for Jaccard similarity on sets. The general warning about high-dimensional neighborhoods is relevant, but the metric and data distribution must match before drawing a conclusion.
