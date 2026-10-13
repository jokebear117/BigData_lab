# Task 2 measurements

- Platform: Linux-6.6.87.2-microsoft-standard-WSL2-x86_64
- CPU: Intel Core Ultra 5 226V
- Python: 3.12.3
- Host RAM: 8082649088 bytes
- Other running work: Codex and measurement Python were running during the measurements. User reports WSL, VS Code and ChatGPT app; other Windows processes were not inspected.
- Stopping reason (A2): For target n=10,240,000, stopped after consuming 9,800,000 items in 30.2029 seconds, exceeding the predeclared 30-second latency threshold. Time became burdensome first; process peak RSS was 750,927,872 bytes, below the 25%-of-WSL-RAM threshold. No out-of-memory failure occurred.

Memory is tracemalloc peak Python allocation, not total process RSS.
Container memory limits may differ from host RAM.

| n | distinct | exact seconds | exact peak bytes | FM seconds | FM peak bytes | FM / truth |
|---:|---:|---:|---:|---:|---:|---:|
| 10000 | 3675 | 0.018 | 313696 | 2.901 | 7588 | 1.495 |
| 40000 | 14665 | 0.077 | 1250919 | 11.559 | 7591 | 1.040 |
| 160000 | 58799 | 0.323 | 5030517 | 42.845 | 7591 | 1.648 |
| 640000 | 235071 | 1.345 | 20539688 | 173.141 | 7594 | 1.446 |

## Additional exact-only stress measurements

Both methods were compared in the table above. The following runs only probe exact-set burden.
Predeclared stopping criteria: 30 seconds or process RSS >= 25% of WSL RAM.
Stopped runs count only consumed items; they are not completed measurements of target n.

| target n | consumed | completed | distinct in consumed prefix | exact seconds | Python peak bytes | process peak RSS bytes |
|---:|---:|:---:|---:|---:|---:|---:|
| 2560000 | 2560000 | True | 940091 | 7.874 | 82368287 | 198737920 |
| 10240000 | 9800000 | False | 3721563 | 30.203 | 331509774 | 750927872 |

RSS includes interpreter and tracemalloc bookkeeping, beyond the set's Python allocations.
Each stress size runs in a fresh Python process.

Endpoint comparison: n increased 64.0x.
- Exact: memory increased 65.48x; empirical exponent 1.01 (memory ~ n^exponent).
- FM: memory increased 1.00x; empirical exponent 0.00 (memory ~ n^exponent).

Expected growth: exact O(distinct), FM O(n_hashes) for fixed 64-bit hashes.
FM accuracy ratios above show estimation error at each size; error need not decrease with n.

These are restored earlier measurements, not a fresh benchmark. Physical laptop RAM reported by the user: 16 GiB; measured WSL RAM: 7.53 GiB.
