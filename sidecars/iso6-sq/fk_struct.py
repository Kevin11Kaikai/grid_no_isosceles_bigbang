"""Structure of a maximum 3-row sq-free set; try F_2 equality plus one point."""
from __future__ import annotations

from sq import can_add, is_sq_free


def eq2(n):
    I = list(range(n - 1))
    return [(x, 0) for x in I] + [(x, n - 1) for x in I]


def try_plus_one(n):
    P0 = set(eq2(n))
    hits = []
    for y in range(1, n - 1):
        for x in range(n):
            if can_add(P0, (x, y)):
                hits.append((x, y))
    return hits


def search_fixed(n, ys):
    k = len(ys)
    best = [0]
    bestP = [set()]

    def rec(x, P, sz):
        if sz + k * (n - x) <= best[0]:
            return
        if x == n:
            if sz > best[0]:
                best[0] = sz
                bestP[0] = set(P)
            return
        for mask in range(1 << k):
            newP = set(P)
            extra = 0
            ok = True
            for i in range(k):
                if mask >> i & 1:
                    p = (x, ys[i])
                    if not can_add(newP, p):
                        ok = False
                        break
                    newP.add(p)
                    extra += 1
            if ok:
                rec(x + 1, newP, sz + extra)

    rec(0, set(), 0)
    return best[0], bestP[0]


def row_sizes(pts, ys):
    from collections import Counter

    c = Counter(p[1] for p in pts)
    return {y: c[y] for y in ys}


def main():
    for n in range(3, 9):
        hits = try_plus_one(n)
        print(f"n={n} eq2+1 addable {len(hits)} {hits[:12]}", flush=True)

    for n in range(3, 8):
        ys = (0, 1, n - 1)
        sz, P = search_fixed(n, ys)
        print(
            f"n={n} rows{ys} max={sz} sizes={row_sizes(P, ys)} "
            f"sq={is_sq_free(P)}",
            flush=True,
        )


if __name__ == "__main__":
    main()
