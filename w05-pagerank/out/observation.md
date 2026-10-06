# Observations

## Task 1
- A dead end's rank vanishes in the uncorrected walk; I redistribute dangling rank uniformly, which conserves total rank. Teleportation also lets the surfer leave a spider trap, so one mechanism fixes both failures.
- `beta` is the probability of following an outgoing link; with probability `1-beta` the surfer teleports uniformly to a page.

## Task 2
- On this graph iterations increased from 14 at beta 0.5 to 24 at 0.99; at 20,000 nodes runtime rose to 0.173 s while iterations stayed near 20. The ordered top 10 first swapped p00000 and p00004 at beta 0.7, although membership stayed fixed.
- Tolerance `1e-6` needed 12 iterations versus 20 for `1e-10`. Machine details and the full curves are in `out/convergence.md`.

## Task 3
- The solver keeps two rank vectors plus six scalar accumulators (2n+6 floats), scattering along the graph's existing adjacency list instead of storing an n×n matrix. It used 2,406 floats versus 1,440,000 dense, ran over 50× faster, and worst rank difference was `1.18e-15`.
- Teleportation adds the same `(1-beta)/n` to every node, so initialize each next-rank entry with that constant; dangling mass is another scalar uniform addition. Neither needs an n×n matrix.
