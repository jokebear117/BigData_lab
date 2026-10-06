#!/usr/bin/env python3
"""Week 3 · Task 3 — Find the same pairs without comparing everything.

Textbook §3.4.

`BruteForce` compares every pair. On 3,000 documents that is 4.5 million
comparisons and it is completely correct. On 3 million documents it is 4.5
trillion and it is completely useless.

Beat it. Find the same near-duplicate pairs while making far fewer comparisons.

    python3 bench.py
    python3 bench.py --yours

The harness counts every call you make to `similarity()`. That is your score.
It also checks **recall** - which of the truly similar pairs you found. Skipping
comparisons is easy; skipping comparisons without losing the pairs is the task.
"""


class BruteForce:
    """Correct, and quadratic."""

    def __init__(self, threshold):
        self.threshold = threshold

    def find(self, docs, similarity):
        """docs is [set_of_shingles, ...]. Return {(i, j), ...} with i < j."""
        out = set()
        for i in range(len(docs)):
            for j in range(i + 1, len(docs)):
                if similarity(docs[i], docs[j]) >= self.threshold:
                    out.add((i, j))
        return out


class YourFinder:
    """Your near-duplicate finder.

        __init__(threshold)
        find(docs, similarity) -> {(i, j), ...}

    `similarity(a, b)` is the only way to compare two documents, and every call
    is counted. Everything else - signatures, banding, bucketing - is free, in
    the sense that the harness does not charge you for it. That is deliberate:
    it is also roughly true at scale, where the comparison is the expensive
    part and the hashing is linear.

    Two knobs decide everything:

        the number of hashes in a signature
        how many bands you split it into

    §3.4.2 gives you the relationship between those and the probability that a
    pair at similarity s becomes a candidate. It is an S-curve, and where its
    step sits is something you choose. Choose it on purpose and be able to say
    why in observation.md - a threshold of 0.8 does not mean bands should be
    anything in particular until you have done the arithmetic.

    You may reuse your Task 1 code.
    """

    # 120 hashes / 30 bands gives 4 rows per band. At s=.6, the
    # candidate probability is 1 - (1 - .6**4)**30 ~= 98.4%.
    HASH_COUNT = 120
    BAND_COUNT = 30
    PRIME = 2_147_483_647

    def __init__(self, threshold):
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")
        self.threshold = threshold

    def find(self, docs, similarity):
        if len(docs) < 2:
            return set()

        # Fixed coefficients make the signatures repeatable across runs.
        import random
        rng = random.Random(314159)
        hashes = [(rng.randrange(1, self.PRIME), rng.randrange(self.PRIME))
                  for _ in range(self.HASH_COUNT)]

        signatures = []
        for doc in docs:
            sig = [self.PRIME] * self.HASH_COUNT
            for shingle in doc:
                for index, (a, b) in enumerate(hashes):
                    value = (a * shingle + b) % self.PRIME
                    if value < sig[index]:
                        sig[index] = value
            signatures.append(sig)

        rows_per_band = self.HASH_COUNT // self.BAND_COUNT
        buckets = {}
        for band in range(self.BAND_COUNT):
            start = band * rows_per_band
            for index, sig in enumerate(signatures):
                key = (band, tuple(sig[start:start + rows_per_band]))
                buckets.setdefault(key, []).append(index)

        candidates = set()
        for members in buckets.values():
            for pos, i in enumerate(members):
                for j in members[pos + 1:]:
                    candidates.add((i, j) if i < j else (j, i))

        return {(i, j) for i, j in candidates
                if similarity(docs[i], docs[j]) >= self.threshold}
