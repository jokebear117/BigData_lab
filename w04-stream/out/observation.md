# Observations

## Task 1
- A Bloom filter has no false negatives because insertion sets every bit queried later; membership is true only when all those bits remain set. With 800 inserts, predicted false-positive rate was 0.860% and measured rate was 0.790% (20,000 absent probes).
- Flajolet–Martin combines groups of four maxima by a median, then takes the median of group estimates; this run estimated 22,178 distinct versus 19,953 (1.11×). On the same hashes, averaging all `2^R` values gave 42,921 (2.15×) as a high register dominated it; one raw median gave 25,346 (1.27×) but is quantized to a power of two.
- Reservoir sampling replaces a selected slot with probability k/(i+1) for item i, using a random index over all items seen so far; it stores only the reservoir and does not need the final stream length.

## Task 2
- Exact counting became costly at 25 million stream items: 79.64 seconds and 744.8 MB traced peak. Across the full 16× comparison, exact memory grew 11.9× while the eight-hash FM sketch stayed near 4 KB; estimate ratios ranged 0.69×–1.64×. See `out/limits.md`.
- A factor-of-two estimate can be enough to size a daily audience or spot a major traffic surge, but not for billing, quotas or detecting a small change; those need an exact count or a more accurate sketch.

## Task 3
- I chose the number of hash probes `k`: minimizing `(1 - e^(-kn/m))^k` gives `k = (m/n) ln 2`; at 10 bits/item this is 6.93, so I use 7. The theoretical floor is `(1/2)^(ln(2)*10) ≈ 0.819%`.
- With 80,000 bits and 8,000 inserted items, the measured rate was 0.831%, close to the floor and well below the 9.511% one-hash baseline; there were zero false negatives. If stream length is unknown, a scalable layered filter can grow as needed; guessing too low raises false positives, while guessing too high reserves unused memory.
