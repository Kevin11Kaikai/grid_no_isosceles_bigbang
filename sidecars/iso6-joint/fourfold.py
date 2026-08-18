"""Four-fold 3-AP-free intersection. Does not import iso6.

S = {(x,y) in [n]^2 : x in A, y in B, x+y in W, x-y in Z}
with A,B,W,Z 3-AP-free. Sufficiency: S is Q4-feasible.
"""
from __future__ import annotations

import random


def is_3ap_free(A):
    s = set(A)
    L = list(s)
    for i, a in enumerate(L):
        for b in L[i + 1 :]:
            if (a + b) % 2 == 0 and (a + b) // 2 in s:
                return False
    return True


def greedy_3ap_free(values, rng=None):
    vals = list(values)
    if rng is not None:
        rng.shuffle(vals)
    B, Bs = [], set()
    for x in vals:
        ok = True
        for a in B:
            if (x + a) % 2 == 0 and (x + a) // 2 in Bs:
                ok = False
                break
            if (2 * x - a) in Bs:
                ok = False
                break
        if ok:
            B.append(x)
            Bs.add(x)
    return sorted(B)


def base3_no_two(limit):
    out = []
    for x in range(limit):
        t, ok = x, True
        while t:
            if t % 3 == 2:
                ok = False
                break
            t //= 3
        if ok:
            out.append(x)
    return out


def build_S(n, A, B, W, Z):
    As, Bs, Ws, Zs = set(A), set(B), set(W), set(Z)
    pts = []
    for x in range(n):
        if x not in As:
            continue
        for y in range(n):
            if y not in Bs:
                continue
            if (x + y) in Ws and (x - y) in Zs:
                pts.append((x, y))
    return pts


def shift_clip(base, shift, lo, hi):
    return [v + shift for v in base if lo <= v + shift < hi]


def dense_fourfold(n, rng, n_tries=40):
    """Search shifts of greedy 3-AP-free sets for a large four-fold S."""
    T = greedy_3ap_free(range(n), rng)
    Tp = greedy_3ap_free(range(2 * n), rng)
    best = None
    for _ in range(n_tries):
        a = rng.randrange(-(n - 1), n)
        b = rng.randrange(-(n - 1), n)
        w = rng.randrange(-(2 * n - 1), 2 * n - 1)
        z = rng.randrange(-(3 * n - 2), n)
        A = shift_clip(T, a, 0, n)
        B = shift_clip(T, b, 0, n)
        W = [v + w for v in Tp]
        Z = [v + z for v in Tp]
        if not (is_3ap_free(A) and is_3ap_free(B) and is_3ap_free(W) and is_3ap_free(Z)):
            continue
        pts = build_S(n, A, B, W, Z)
        rec = {
            "n": n,
            "shifts": (a, b, w, z),
            "|T|": len(T),
            "|Tp|": len(Tp),
            "|A|": len(A),
            "|B|": len(B),
            "|W|": len(W),
            "|Z|": len(Z),
            "|S|": len(pts),
            "set": pts,
        }
        if best is None or rec["|S|"] > best["|S|"]:
            best = rec
    return best


def can_add_3ap(Bs, x):
    for a in Bs:
        if (x + a) % 2 == 0 and (x + a) // 2 in Bs:
            return False
        if (2 * x - a) in Bs:
            return False
    return True


def greedy_3ap_weighted(weighted, rng=None):
    """Add values in decreasing-weight order (optional jitter), keep 3-AP-free."""
    items = list(weighted)
    if rng is not None:
        rng.shuffle(items)
        items.sort(key=lambda kv: -kv[1])
    else:
        items.sort(key=lambda kv: -kv[1])
    B, Bs = [], set()
    for x, _w in items:
        if can_add_3ap(Bs, x):
            B.append(x)
            Bs.add(x)
    return sorted(B)


def smallest_3ap_free(lo, hi):
    return greedy_3ap_free(range(lo, hi), rng=None)


def fourfold_freq(n, A, B, rng=None, z_first=False):
    """A,B 3-AP-free; choose W,Z as popular 3-AP-free sums/diffs of A×B."""
    pairs = [(x, y) for x in A for y in B]
    if not z_first:
        from collections import Counter

        sc = Counter(x + y for x, y in pairs)
        W = greedy_3ap_weighted(list(sc.items()), rng)
        Ws = set(W)
        pairs = [(x, y) for x, y in pairs if x + y in Ws]
        dc = Counter(x - y for x, y in pairs)
        Z = greedy_3ap_weighted(list(dc.items()), rng)
        Zs = set(Z)
        pts = [(x, y) for x, y in pairs if x - y in Zs]
    else:
        from collections import Counter

        dc = Counter(x - y for x, y in pairs)
        Z = greedy_3ap_weighted(list(dc.items()), rng)
        Zs = set(Z)
        pairs = [(x, y) for x, y in pairs if x - y in Zs]
        sc = Counter(x + y for x, y in pairs)
        W = greedy_3ap_weighted(list(sc.items()), rng)
        Ws = set(W)
        pts = [(x, y) for x, y in pairs if x + y in Ws]
    return {
        "n": n,
        "kind": "freq_zfirst" if z_first else "freq",
        "|A|": len(A),
        "|B|": len(B),
        "|W|": len(W),
        "|Z|": len(Z),
        "|S|": len(pts),
        "set": pts,
    }


def dense_fourfold_from_bases(n, rng, n_tries=40):
    """Independent greedy 3-AP-free A,B on [n] and W,Z on a wide interval."""
    best = None
    for _ in range(n_tries):
        A = greedy_3ap_free(range(n), rng)
        B = greedy_3ap_free(range(n), rng)
        W = greedy_3ap_free(range(-1, 2 * n), rng)
        Z = greedy_3ap_free(range(1 - n, n), rng)
        pts = build_S(n, A, B, W, Z)
        rec = {
            "n": n,
            "kind": "indep",
            "|A|": len(A),
            "|B|": len(B),
            "|W|": len(W),
            "|Z|": len(Z),
            "|S|": len(pts),
            "set": pts,
        }
        if best is None or rec["|S|"] > best["|S|"]:
            best = rec
    return best


def dense_fourfold_freq_search(n, rng, n_tries=60):
    """Search A,B (smallest-first + shuffled) then frequency-greedy W,Z."""
    best = None
    A0 = smallest_3ap_free(0, n)
    B0 = smallest_3ap_free(0, n)
    for z_first in (False, True):
        rec = fourfold_freq(n, A0, B0, rng=None, z_first=z_first)
        if best is None or rec["|S|"] > best["|S|"]:
            best = rec
    for _ in range(n_tries):
        A = greedy_3ap_free(range(n), rng)
        B = greedy_3ap_free(range(n), rng)
        for z_first in (False, True):
            rec = fourfold_freq(n, A, B, rng=rng, z_first=z_first)
            if best is None or rec["|S|"] > best["|S|"]:
                best = rec
    return best
