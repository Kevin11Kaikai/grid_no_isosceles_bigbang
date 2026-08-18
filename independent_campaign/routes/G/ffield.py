"""Minimal F_p linear algebra (p prime) used by the rank / slice-rank experiments."""
import itertools


def rank_mod_p(M, p):
    """Row-reduce a list-of-lists matrix over F_p; return its rank."""
    M = [row[:] for row in M]
    rows, cols = len(M), len(M[0]) if M else 0
    r = 0
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if M[i][c] % p:
                piv = i
                break
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        inv = pow(M[r][c], p - 2, p)
        M[r] = [(v * inv) % p for v in M[r]]
        for i in range(rows):
            if i != r and M[i][c] % p:
                f = M[i][c]
                M[i] = [(M[i][j] - f * M[r][j]) % p for j in range(cols)]
        r += 1
        if r == rows:
            break
    return r


def rank_exact_int(M):
    """Exact rank over Q using Fraction-free Gaussian elimination."""
    from fractions import Fraction
    M = [[Fraction(v) for v in row] for row in M]
    rows = len(M)
    cols = len(M[0]) if M else 0
    r = 0
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if M[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        pv = M[r][c]
        M[r] = [v / pv for v in M[r]]
        for i in range(rows):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [M[i][j] - f * M[r][j] for j in range(cols)]
        r += 1
        if r == rows:
            break
    return r


def symmetric_forms_dim(d, p):
    """All symmetric d x d matrices over F_p, up to nothing (used only for tiny d)."""
    idx = [(i, j) for i in range(d) for j in range(i, d)]
    for vals in itertools.product(range(p), repeat=len(idx)):
        G = [[0] * d for _ in range(d)]
        for (i, j), v in zip(idx, vals):
            G[i][j] = v
            G[j][i] = v
        yield G
