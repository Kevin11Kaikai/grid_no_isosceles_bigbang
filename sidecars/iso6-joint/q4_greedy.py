"""Independent Q4-greedy corpus. Regenerated here; does not read routes/Q."""
from __future__ import annotations

import random

from q4 import greedy, verify


def sample_q4_greedy(n, n_sets, seed):
    rng = random.Random(seed)
    out = []
    for i in range(n_sets):
        pts = greedy(n, rng)
        rec = {"n": n, "i": i, "|S|": len(pts), "set": list(pts), "q4": verify(n, pts)}
        out.append(rec)
    return out
