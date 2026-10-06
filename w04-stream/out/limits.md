# Exact counting versus a bounded sketch

- Machine: Windows 11 x64, Intel Core Ultra 5 226V, 15.54 GiB RAM, Python 3.12.10. Codex, a browser and normal desktop applications were open; measurements were not isolated from other workloads.
- The exact column holds distinct strings in a Python `set`; memory is tracemalloc peak. The sketch uses eight FM hashes for this larger measurement, while Task 1's accuracy check uses the default 64.

| Stream n | Exact time (s) | Exact peak (MB) | FM time (s) | FM peak (bytes) | FM estimate / truth |
|---:|---:|---:|---:|---:|---:|
| 100,000 | 0.20 | 3.93 | 5.24 | 3,946 | 1.38× |
| 200,000 | 0.59 | 5.76 | 12.78 | 3,946 | 0.86× |
| 400,000 | 1.18 | 11.59 | 26.06 | 3,948 | 1.64× |
| 1,600,000 | 4.90 | 46.65 | 103.30 | 4,012 | 0.69× |

From 100,000 to 1,600,000 items (16×), the exact set's peak grew 11.9× and its measured time grew 24.7×. The sketch's retained peak changed by only 66 bytes (about 1.7%), staying near 4 KB because it stores hash maxima rather than stream items. Its estimates ranged from 0.69× to 1.64× of truth; the error did not steadily improve with a larger stream.

## Where exact counting became unpleasant

I extended the exact-only run to 25,000,000 stream items (about 9,179,304 distinct strings). It completed in 79.64 seconds and peaked at 744,836,356 traced bytes (744.8 MB). On this 15.54 GiB machine, time was the first practical limit; the process did not exhaust RAM or fail. I stopped there rather than spend several more minutes scaling the exact set further. The largest full exact-versus-FM comparison remains 1.6 million because the eight-hash sketch takes 103 seconds at that size.
