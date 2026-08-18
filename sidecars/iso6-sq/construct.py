"""Construction battery against Q_SQ. Does not import iso6 / Q / iso6-joint."""
from __future__ import annotations

import random

from sq import (
    can_add,
    count_square_corners,
    is_sq_free,
    repair_delete_participants,
    repair_sq_free,
)


def rec(name, n, pts, extra=None):
    pts = list(map(tuple, pts))
    m = len(pts)
    free = is_sq_free(pts)
    d = {
        "family": name,
        "n": n,
        "|S|": m,
        "|S|/n": (m / n) if n else 0.0,
        "sq_free": free,
    }
    if free:
        d["n_corners"] = 0
    elif m <= 1200:
        d["n_corners"] = count_square_corners(pts)
    else:
        d["n_corners"] = None
        d["n_corners_note"] = "skipped_count_large_nonfree"
    if extra:
        d.update(extra)
    return d, pts


def base3_no_two(limit):
    out = []
    for x in range(max(0, limit)):
        t, ok = x, True
        while t:
            if t % 3 == 2:
                ok = False
                break
            t //= 3
        if ok:
            out.append(x)
    return out


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


def is_3ap_free(A):
    s = set(A)
    L = list(s)
    for i, a in enumerate(L):
        for b in L[i + 1 :]:
            if (a + b) % 2 == 0 and (a + b) // 2 in s:
                return False
    return True


# --- negative controls ---


def bxB(n):
    B = base3_no_two(n)
    pts = [(x, y) for x in B for y in B]
    return rec("BxB", n, pts, extra={"|B|": len(B)})


def fourfold_greedy(n, rng):
    A = greedy_3ap_free(range(n), rng)
    B = greedy_3ap_free(range(n), rng)
    W = greedy_3ap_free(range(0, 2 * n), rng)
    Z = greedy_3ap_free(range(1 - n, n), rng)
    As, Bs, Ws, Zs = set(A), set(B), set(W), set(Z)
    pts = [
        (x, y)
        for x in range(n)
        for y in range(n)
        if x in As and y in Bs and (x + y) in Ws and (x - y) in Zs
    ]
    return rec(
        "fourfold",
        n,
        pts,
        extra={
            "|A|": len(A),
            "|B|": len(B),
            "|W|": len(W),
            "|Z|": len(Z),
            "3ap": all(map(is_3ap_free, (A, B, W, Z))),
        },
    )


def fourfold_freq(n, rng):
    """A,B greedy 3-AP-free; W,Z = popular 3-AP-free sums/diffs of A×B."""
    from collections import Counter

    A = greedy_3ap_free(range(n), rng)
    B = greedy_3ap_free(range(n), rng)
    pairs = [(x, y) for x in A for y in B]
    sc = Counter(x + y for x, y in pairs)
    W, Ws = [], set()
    for s, _ in sorted(sc.items(), key=lambda kv: -kv[1]):
        ok = True
        for a in W:
            if (s + a) % 2 == 0 and (s + a) // 2 in Ws:
                ok = False
                break
            if (2 * s - a) in Ws:
                ok = False
                break
        if ok:
            W.append(s)
            Ws.add(s)
    pairs = [(x, y) for x, y in pairs if x + y in Ws]
    dc = Counter(x - y for x, y in pairs)
    Z, Zs = [], set()
    for d, _ in sorted(dc.items(), key=lambda kv: -kv[1]):
        ok = True
        for a in Z:
            if (d + a) % 2 == 0 and (d + a) // 2 in Zs:
                ok = False
                break
            if (2 * d - a) in Zs:
                ok = False
                break
        if ok:
            Z.append(d)
            Zs.add(d)
    pts = [(x, y) for x, y in pairs if x - y in Zs]
    return rec(
        "fourfold_freq",
        n,
        pts,
        extra={"|A|": len(A), "|B|": len(B), "|W|": len(W), "|Z|": len(Z)},
    )


def j1_embed_fourfold(n=16):
    """Three-point four-fold realizing the smallest Q4-surviving square-corner u=(3,2)."""
    u, v = (3, 2), (-2, 3)
    raw = [(0, 0), u, v]
    minx = min(p[0] for p in raw)
    miny = min(p[1] for p in raw)
    pts = [(p[0] - minx, p[1] - miny) for p in raw]
    need = max(max(p[0] for p in pts), max(p[1] for p in pts)) + 1
    if need > n:
        n = need
    A = sorted({x for x, _y in pts})
    B = sorted({y for _x, y in pts})
    W = sorted({x + y for x, y in pts})
    Z = sorted({x - y for x, y in pts})
    return rec(
        "fourfold_J1_embed",
        n,
        pts,
        extra={
            "A": A,
            "B": B,
            "W": W,
            "Z": Z,
            "3ap": all(map(is_3ap_free, (A, B, W, Z))),
        },
    )


# --- function graphs ---


def graph_linear(n, a=1, b=0):
    pts = [(x, (a * x + b) % n) for x in range(n)]
    return rec("graph_linear", n, pts, extra={"a": a, "b": b})


def graph_quadratic(n, a=1, b=0, c=0):
    pts = [(x, (a * x * x + b * x + c) % n) for x in range(n)]
    return rec("graph_quadratic", n, pts, extra={"a": a, "b": b, "c": c})


def graph_cubic(n):
    pts = [(x, (x * x * x + x) % n) for x in range(n)]
    return rec("graph_cubic", n, pts)


def graph_parabola_embed(n):
    """{(t, t^2) : t^2 < n} inside [n]^2. Size ~sqrt(n)."""
    pts = []
    t = 0
    while t * t < n:
        pts.append((t, t * t))
        t += 1
    return rec("graph_parabola_embed", n, pts)


# --- at most 2 per row/col ---


def greedy_2_per_rowcol(n, rng, also_sq=True):
    cells = [(x, y) for x in range(n) for y in range(n)]
    rng.shuffle(cells)
    P = set()
    row_c = [0] * n
    col_c = [0] * n
    for x, y in cells:
        if row_c[y] >= 2 or col_c[x] >= 2:
            continue
        if also_sq and not can_add(P, (x, y)):
            continue
        P.add((x, y))
        row_c[y] += 1
        col_c[x] += 1
    name = "greedy_2rc_sq" if also_sq else "greedy_2rc"
    return rec(name, n, P)


def greedy_sq_free(n, rng):
    """Independent greedy sq-free baseline. Comparator only; never a status change."""
    cells = [(x, y) for x in range(n) for y in range(n)]
    rng.shuffle(cells)
    P = set()
    for p in cells:
        if can_add(P, p):
            P.add(p)
    return rec("greedy_sq_free", n, P)


# --- Sidon / convex products ---


def greedy_sidon(n, rng=None):
    vals = list(range(n))
    if rng is not None:
        rng.shuffle(vals)
    else:
        vals.sort()
    A, diffs = [], set()
    for x in vals:
        ok = True
        for a in A:
            d = x - a
            if d in diffs:
                ok = False
                break
        if ok:
            for a in A:
                diffs.add(x - a)
            A.append(x)
    return sorted(A)


def product_set(n, A, B, name):
    As = [a for a in A if 0 <= a < n]
    Bs = [b for b in B if 0 <= b < n]
    pts = [(x, y) for x in As for y in Bs]
    d, pts = rec(name, n, pts, extra={"|A|": len(As), "|B|": len(Bs)})
    return d, pts


def convex_squares(n):
    return [i * i for i in range(n) if i * i < n]


def convex_cubes(n):
    return [i * i * i for i in range(n) if i * i * i < n]


# --- classical-corner-free (diagonal 3-AP-free) then repair ---


def classical_corner_free(n):
    """S = {(x,y): y-x in B}, B 3-AP-free on the diagonal range.

    Axis-aligned corners (x,y), (x+d,y), (x,y+d) force a 3-AP in B.
    """
    B = base3_no_two(2 * n)
    B = [b - n for b in B]  # shift into [-n, n)
    Bs = set(B)
    pts = [(x, y) for x in range(n) for y in range(n) if (y - x) in Bs]
    extra = {"|B|": len(Bs), "B_3ap": is_3ap_free(B)}
    return rec("classical_corner_free", n, pts, extra=extra)


def behrend_like_rows(n):
    """Full rows indexed by a 3-AP-free set. Large, expected many rotated corners."""
    B = base3_no_two(n)
    pts = [(x, y) for y in B for x in range(n)]
    return rec("full_rows_3ap", n, pts, extra={"|B|": len(B)})


# --- modular ---


def mod_inv(a, p):
    return pow(a, p - 2, p)


def is_prime(p):
    if p < 2:
        return False
    if p % 2 == 0:
        return p == 2
    d = 3
    while d * d <= p:
        if p % d == 0:
            return False
        d += 2
    return True


def prev_prime(n):
    p = n if n % 2 else n - 1
    while p >= 3 and not is_prime(p):
        p -= 2
    return max(p, 2)


def hyperbola(n, k=1):
    p = prev_prime(n)
    pts = []
    for x in range(1, p):
        y = (k * mod_inv(x, p)) % p
        if y < n and x < n:
            pts.append((x, y))
    return rec("hyperbola", n, pts, extra={"p": p, "k": k})


def quadratic_residues_graph(n):
    p = prev_prime(n)
    pts = [(x, (x * x) % p) for x in range(p) if x < n and (x * x) % p < n]
    return rec("quad_res_graph", n, pts, extra={"p": p})


def repair_record(name, n, pts, mode="auto"):
    before = len(pts)
    n_c = count_square_corners(pts) if before <= 1200 else None
    if mode == "auto":
        mode = "participants" if before > 600 else "degree"
    if mode == "participants":
        P, deleted, leftover = repair_delete_participants(pts)
        tag = name + "+repair_hit"
    else:
        P, deleted, leftover = repair_sq_free(pts, max_rounds=40)
        tag = name + "+repair"
    d, _ = rec(
        tag,
        n,
        P,
        extra={
            "|S|_before": before,
            "n_corners_before": n_c,
            "deleted": deleted,
            "leftover_corners": leftover,
        },
    )
    return d, list(P)
