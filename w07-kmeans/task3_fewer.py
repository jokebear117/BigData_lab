#!/usr/bin/env python3
"""Week 7 · Task 3 — The same clustering, with far fewer distances.

Textbook §7.3, and §7.1.3 for why distance is the expensive part.

`NaiveKMeans` does what the definition says: every iteration, compare every
point with every centroid. That is n x k distance computations per pass, and on
a real dataset the distance computation is almost the entire cost.

Most of that work is wasted. After the first couple of iterations, most points
do not change cluster, and most centroids barely move. The triangle inequality
lets you prove a point cannot have changed cluster **without measuring it**.

    python3 bench.py
    python3 bench.py --yours

Correctness first: your final SSE must match the baseline's. Fewer distances
with a worse clustering is not an improvement, it is a different algorithm.
"""


class NaiveKMeans:
    """Every point against every centroid, every iteration."""

    def __init__(self, k, max_iter=50):
        self.k, self.max_iter = k, max_iter

    def run(self, points, initial_centroids, distance):
        centroids = list(initial_centroids)
        labels = [None] * len(points)
        for self.iterations in range(1, self.max_iter + 1):
            changed = False
            for i, p in enumerate(points):
                best, bi = None, 0
                for j, c in enumerate(centroids):
                    d = distance(p, c)
                    if best is None or d < best - 1e-12:
                        best, bi = d, j
                if labels[i] != bi:
                    labels[i] = bi
                    changed = True
            centroids = _means(points, labels, self.k, centroids)
            if not changed:
                break
        return labels, centroids


def _means(points, labels, k, previous):
    out = []
    for j in range(k):
        group = [p for p, l in zip(points, labels) if l == j]
        if group:
            out.append(tuple(sum(v) / len(group) for v in zip(*group)))
        else:
            out.append(previous[j])
    return out


class YourKMeans:
    """Your k-means.

        __init__(k, max_iter=50)
        run(points, initial_centroids, distance) -> (labels, centroids)

    Same starting centroids, same `distance` function - which is counted. That
    counter is your score.

    The idea, from §7.3 and the triangle inequality:

        if a point is much closer to its current centroid than that centroid
        moved, and than any other centroid could have come, then it cannot have
        changed cluster, and you do not have to measure anything

    Keeping enough bookkeeping to make that test cheap, without keeping so much
    that the bookkeeping costs more than the distances, is the task.

    You may call `distance` on two centroids, and those calls are counted too -
    which is the correct accounting, since that is real work. There are k of
    them and n points, and k is much smaller than n. That asymmetry is the
    whole opening.
    """

    def __init__(self, k, max_iter=50):
        self.k, self.max_iter = k, max_iter
        self.iterations = 0

    def run(self, points, initial_centroids, distance):
        points = list(points)
        centroids = list(initial_centroids)
        n, k = len(points), self.k
        labels = [0] * n
        upper = [0.0] * n
        lower = [0.0] * n

        # Initial assignment is exact; it also establishes each point's
        # distance to its assigned centre and nearest competing centre.
        for i, point in enumerate(points):
            ds = [distance(point, c) for c in centroids]
            order = sorted(range(k), key=lambda j: (ds[j], j))
            labels[i] = order[0]
            upper[i] = ds[order[0]]
            lower[i] = ds[order[1]] if k > 1 else float("inf")

        for iteration in range(1, self.max_iter + 1):
            moved_centroids = _means(points, labels, k, centroids)
            shifts = [distance(a, b) for a, b in zip(centroids, moved_centroids)]
            max_shift = max(shifts, default=0.0)
            # Update triangle-inequality bounds after the centres move.
            for i, label in enumerate(labels):
                upper[i] += shifts[label]
                lower[i] = max(0.0, lower[i] - max_shift)
            centroids = moved_centroids
            separation = [float("inf")] * k
            for a in range(k):
                for b in range(a + 1, k):
                    half = distance(centroids[a], centroids[b]) / 2
                    separation[a] = min(separation[a], half)
                    separation[b] = min(separation[b], half)

            changed = False
            for i, point in enumerate(points):
                old = labels[i]
                if upper[i] <= max(lower[i], separation[old]):
                    continue
                own = distance(point, centroids[old])
                best, best_label = own, old
                second = float("inf")
                for j, center in enumerate(centroids):
                    if j == old:
                        continue
                    d = distance(point, center)
                    if d < best - 1e-12 or (abs(d - best) <= 1e-12 and j < best_label):
                        second, best, best_label = best, d, j
                    else:
                        second = min(second, d)
                if best_label != old:
                    changed = True
                labels[i] = best_label
                upper[i] = best
                # Conservative lower bound to any competing centre.
                lower[i] = second if second != float("inf") else float("inf")
            self.iterations = iteration
            if not changed:
                break
        return labels, centroids
