#!/usr/bin/env python3
"""Week 4 · Task 3 — Same memory, fewer mistakes.

Textbook §4.4 (Bloom filters), §4.5 (counting distinct).

`NaiveFilter` is a membership filter in a fixed number of bits. It works. It
also makes far more mistakes than it has to with the memory it was given, and
it does so for a reason you can find by reading §4.4.2 and doing one derivative.

You get **exactly the same number of bits**. Make fewer mistakes.

    python3 bench.py
    python3 bench.py --yours

The rule that makes this interesting: a false negative is not allowed. Ever.
The whole point of this structure is that "no" means no. A filter that gets a
better score by occasionally forgetting something it was given has not improved
anything, it has broken the contract.
"""
import hashlib, math, sys

from task1_sketches import BloomFilter


class NaiveFilter:
    """One hash function, and the bits it was given."""

    def __init__(self, n_bits, seed=246):
        self.n_bits = n_bits
        self.seed = seed
        self.bits = bytearray(n_bits)

    def _index(self, item):
        d = hashlib.blake2b(str(item).encode(), digest_size=8,
                            key=str(self.seed).encode()).digest()
        return int.from_bytes(d, "big") % self.n_bits

    def add(self, item):
        self.bits[self._index(item)] = 1

    def __contains__(self, item):
        return bool(self.bits[self._index(item)])

    def memory_bits(self):
        return self.n_bits


class YourFilter(BloomFilter):
    """Your filter.

        __init__(n_bits, seed=246)
        add(item)
        item in filter  ->  bool
        memory_bits()   ->  how many bits you are using

    `memory_bits()` must not exceed the `n_bits` you were given. The harness
    checks. Counting only some of your memory is not an optimisation.

    §4.4.2 gives the false-positive rate of a filter with m bits, k hashes and
    n items inserted. There is a k that minimises it, and it depends on m/n.
    The harness tells you n before you start, so you have no excuse for guessing.

    Then there is a second question, which is worth more: the harness inserts
    a **known** number of items, but a real stream does not tell you n in
    advance. What would you do then? You do not have to implement it - but
    observation.md asks.
    """

    __slots__ = ()

    def __init__(self, n_bits, seed=246):
        # The assignment harness inserts 8,000 items. k* = (m/n) ln(2).
        # Reserve space for Python object/bytearray/parameter overhead too.
        super().__init__(max(1, n_bits), 1, seed)
        overhead = self.memory_bits() - len(self.bits) * 8
        n_bytes = (n_bits - overhead) // 8
        if n_bytes <= 0:
            raise ValueError("budget is too small for the filter's metadata")
        self.bits = bytearray(n_bytes)
        self.m = n_bytes * 8
        self.k = max(1, round(self.m / 8_000 * math.log(2)))
        # Recheck because Python integer storage can change with magnitude.
        while self.memory_bits() > n_bits and self.bits:
            self.bits.pop()
            self.m = len(self.bits) * 8
        if not self.bits:
            raise ValueError("budget is too small for the filter's metadata")

    def add(self, item):
        super().add(item)

    def __contains__(self, item):
        return super().__contains__(item)

    def memory_bits(self):
        # Count all persistent instance state, including Python overhead.
        values = (self, self.bits, self.m, self.k, self.seed)
        unique = {id(value): value for value in values}
        return sum(sys.getsizeof(value) for value in unique.values()) * 8
