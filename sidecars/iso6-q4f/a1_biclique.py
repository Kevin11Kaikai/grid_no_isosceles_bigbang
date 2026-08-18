"""How large a complete (d,δ) biclique can S* carry?"""
from __future__ import annotations

from q4 import FourDir, verify


def fibre_points(n, a, d, deltas):
    pts = []
    for v in list(deltas) + [-x for x in deltas]:
        alpha = a + v
        if (alpha + d) % 2:
            return None
        x = (alpha + d) // 2
        y = (alpha - d) // 2
        if not (0 <= x < n and 0 <= y < n):
            return None
        pts.append((x, y))
    return pts


def greedy_symmetric_apfree(limit, parity):
    """Greedy 3-AP-free Δ of given parity such that {±δ} is 3-AP-free."""
    s = []
    for x in range(parity if parity else 2, limit + 1, 2):
        trial = s + [x]
        vals = [-d for d in trial] + trial
        ss = set(vals)
        ok = True
        for i, a in enumerate(vals):
            for b in vals[i + 1 :]:
                mid = (a + b) // 2
                if (a + b) % 2 == 0 and mid in ss:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            s.append(x)
    return s


def max_biclique(n, a, deltas):
    st = FourDir(n)
    used = 0
    for d in range(1 - n, n):
        pts = fibre_points(n, a, d, deltas)
        if pts is None:
            continue
        recs = []
        ok = True
        for p in pts:
            ks = st.can_add(*p)
            if ks is None:
                ok = False
                break
            recs.append(st.push(*p, ks))
        if not ok:
            for rec in reversed(recs):
                st.pop(rec)
            continue
        used += 1
    if used and not verify(n, st.pts):
        raise RuntimeError("verify failed")
    return used, 2 * used * len(deltas)


def main():
    for n in (32, 48, 81, 128):
        a = n - 1
        pool = greedy_symmetric_apfree(n // 2, 1 if a % 2 == 0 else 0)
        # a even => need odd deltas so a+delta odd? Wait: all a±δ same parity as a+δ
        # and same as each other. δ same parity. a and a+2δ same. Fine any parity of δ
        # as long as all δ share parity. Choose parity so a+δ and d can be even.
        # Try both parities below if pool is short.
        # anti-value a+delta has parity a+delta; all anti-values on a diagonal
        # have parity of a+d. deltas same parity.
        # use prefix of pool as Δ
        print(f"--- n={n} a={a} pool={len(pool)} ---", flush=True)
        for t in (1, 2, 3, 4, 5, 6, 8, 10, 12):
            if t > len(pool):
                break
            deltas = tuple(pool[:t])
            k, sstar = max_biclique(n, a, deltas)
            print(
                f"  t={t:2d} Δ={deltas}  k={k:3d} |S*|_rect={sstar:4d}  k*t={k*t}",
                flush=True,
            )


if __name__ == "__main__":
    main()
