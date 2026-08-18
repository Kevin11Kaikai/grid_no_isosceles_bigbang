"""Gaussian-integer Salem–Spencer peeling (Károlyi–Solymosi, smallest example).

Base β = 2+2i, alphabet P = {0, 1, i}, peeling order 1, 0, i.
Φ(w) = Σ_j w_j β^j.  A fixed composition class is IRT-free by Theorem 2.6.

Does not import iso6. Checker: sq.py.
"""
from __future__ import annotations

from collections import Counter
from itertools import permutations
from math import log


def gmul(a, b):
    """(re, im) Gaussian integer multiply."""
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def gadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def gpow_beta(j, beta=(2, 2)):
    acc = (1, 0)
    for _ in range(j):
        acc = gmul(acc, beta)
    return acc


BETA = (2, 2)
# peeling order p1, p2, p3
PEEL = ((1, 0), (0, 0), (0, 1))  # 1, 0, i
DIGIT = {0: (0, 0), 1: (1, 0), 2: (0, 1)}  # indices into PEEL for generation


def phi(word, beta=BETA):
    s = (0, 0)
    pw = (1, 0)
    for w in word:
        s = gadd(s, gmul(w, pw))
        pw = gmul(pw, beta)
    return s


def composition_class(m, counts):
    """All words in P^m with given counts of (1,0,i) in peeling order.

    counts = (n1, n0, ni) summing to m, matching PEEL order.
    """
    seq = []
    for p, c in zip(PEEL, counts):
        seq.extend([p] * c)
    # unique permutations
    return set(permutations(seq))


def balanced_counts(m):
    q = 3
    base, r = divmod(m, q)
    counts = [base] * q
    for i in range(r):
        counts[i] += 1
    return tuple(counts)


def build_Am(m):
    counts = balanced_counts(m)
    words = composition_class(m, counts)
    pts = [phi(w) for w in words]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    minx, miny = min(xs), min(ys)
    shifted = [(x - minx, y - miny) for x, y in pts]
    n = 1 + max(max(x for x, _y in shifted), max(y for _x, y in shifted))
    return {
        "m": m,
        "counts": counts,
        "n_words": len(words),
        "|S|": len(set(shifted)),
        "n": n,
        "|S|/n": len(set(shifted)) / n if n else 0.0,
        "exponent": (log(len(set(shifted))) / log(n)) if n > 1 and shifted else 0.0,
        "theory_alpha": 2 * log(3) / (3 * log(2)),  # log 3 / log(2√2)
        "set": list(set(shifted)),
        "bbox": (minx, miny, minx + n - 1, miny + n - 1),
    }


def eq_zi(a, b, c):
    """a + i c == (1+i) b  as Gaussian integers (re, im)."""
    # a + i c = (ar - c_im, ai + cr) wait c=(cr,ci), i*c = (-ci, cr)
    lhs = (a[0] - c[1], a[1] + c[0])
    # (1+i)b = (1,1)*b = (br-bi, br+bi)
    rhs = (b[0] - b[1], b[0] + b[1])
    return lhs == rhs
