# Crossover measurements

- Platform: Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.39
- CPU: Intel(R) Core(TM) Ultra 5 226V
- RAM: 8082653184 bytes
- Python: 3.12.3
- Other workloads running: WSL active; user reports it uses a substantial share of RAM

| n | brute (s) | brute comparisons | brute peak (MiB) | LSH (s) | LSH comparisons | LSH peak (MiB) |
|---:|---:|---:|---:|---:|---:|---:|
| 250 | 0.1758 | 31125 | 0.01 | 4.1936 | 1 | 3.00 |
| 500 | 0.6999 | 124750 | 0.01 | 8.4809 | 7 | 5.93 |
| 1000 | 2.7844 | 499500 | 0.01 | 16.9476 | 27 | 12.39 |
| 2000 | 11.9455 | 1999000 | 0.02 | 34.0980 | 111 | 25.13 |
| 4000 | 47.8117 | 7998000 | 0.02 | 69.2185 | 132 | 50.84 |
| 8000 | 185.0878 | 31996000 | 0.02 | 129.3787 | 147 | 102.31 |

## Brute-force doubling check

- n=250 → 500: time ratio 3.98x (quadratic expectation: ~4x).
- n=500 → 1000: time ratio 3.98x (quadratic expectation: ~4x).
- n=1000 → 2000: time ratio 4.29x (quadratic expectation: ~4x).
- n=2000 → 4000: time ratio 4.00x (quadratic expectation: ~4x).
- n=4000 → 8000: time ratio 3.87x (quadratic expectation: ~4x).
- Observed doubling ratios ranged from 3.87x to 4.29x; this is consistent with roughly quadratic growth.

## Unpleasant size and memory scope

- First measured size taking at least 60 seconds: n=4000 (LSH).
- Peak memory below is additional memory tracked during find(); the input documents were built before tracing and are excluded.

## Crossover and largest measurement

- Brute force is faster through n=4000; LSH first wins at n=8000.
- Largest n=8000: brute peak 0.02 MiB; LSH peak 102.31 MiB.

At small n, brute force wins because it avoids the per-document signature and band-hashing setup. Here LSH computes 120 hash minima for each of 60 shingles per document, then builds 30 band buckets; that linear setup is expensive until pair comparisons dominate.
