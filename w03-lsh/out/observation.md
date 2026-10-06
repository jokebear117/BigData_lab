# Observations

## Task 1
- Minhash scans each row once and updates only columns containing that row, avoiding a separate matrix scan per document.
- When signature length does not divide evenly by the band count, remainder rows are distributed across the first bands so no signature positions are discarded.
- S1–S4 estimate 1.0 from two hashes although the true Jaccard similarity is 2/3; more hashes narrow this sampling error at the cost of signature work.

## Task 2
- On Intel Core Ultra 5 226V with 8.08 GB visible to WSL, brute force was faster through n=4,000; LSH first won at n=8,000. WSL was using a substantial share of RAM.
- Doubling n took 3.87–4.29x as long for brute force, consistent with quadratic growth. At n=8,000 brute force took 185.09s and LSH took 129.38s; LSH additional traced peak was 102.31 MiB.
- LSH first exceeded one minute at n=4,000 (69.22s); at n=8,000 brute force took 185.09s. Small inputs pay the fixed per-document cost of 120 hash minima per shingle and 30 band buckets.

## Task 3
- With 120 hashes and 30 bands (4 rows per band), the S-curve step is (1/30)^(1/4) ≈ 0.427; at s=0.6 candidate probability is about 98.4%, intentionally below the threshold to favor recall.
- The harness found all 121 true pairs (100.0% recall) with 127 comparisons instead of 2,246,140, avoiding 99.99% of comparisons.
- Hashing is excluded from the harness score, but scales with documents × shingles × hashes; for sufficiently large collections that signature-building cost will matter too.
