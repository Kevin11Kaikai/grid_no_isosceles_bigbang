"""Place S* K_{2,3}: two diagonals, three common same-parity deltas."""
from __future__ import annotations

from q4 import FourDir, verify


def doubled_apfree(deltas):
    vals = [-x for x in deltas] + list(deltas)
    ss = set(vals)
    for i, a in enumerate(vals):
        for b in vals[i + 1 :]:
            if (a + b) % 2 == 0 and (a + b) // 2 in ss:
                return False
    return True


def fibre(n, a, d, deltas):
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


def A_minus_A(a, deltas):
    A = [a + d for d in deltas] + [a - d for d in deltas]
    diffs = set()
    for i, u in enumerate(A):
        for v in A[i + 1 :]:
            diffs.add(u - v)
            diffs.add(v - u)
    return diffs


def try_k23(n, a, deltas):
    if not doubled_apfree(deltas):
        return None
    forbidden = A_minus_A(a, deltas)
    diags = []
    for d in range(1 - n, n):
        pts = fibre(n, a, d, deltas)
        if pts is not None:
            diags.append((d, pts))
    for i, (d1, p1) in enumerate(diags):
        for d2, p2 in diags[i + 1 :]:
            if (d1 - d2) in forbidden:
                continue
            st = FourDir(n)
            ok = True
            for p in p1 + p2:
                ks = st.can_add(*p)
                if ks is None:
                    ok = False
                    break
                st.push(*p, ks)
            if ok:
                assert verify(n, st.pts)
                return {"n": n, "a": a, "deltas": deltas, "d1": d1, "d2": d2, "|pts|": 12}
    return None


def main():
    found = 0
    tried = 0
    samples = [
        (1, 5, 13),
        (1, 5, 17),
        (1, 7, 19),
        (2, 8, 22),
        (2, 10, 26),
        (4, 10, 28),
        (1, 5, 25),
        (3, 9, 27),
        (2, 8, 32),
        (1, 13, 37),
    ]
    for n in (32, 48, 81, 128, 243):
        for a in (n - 1, n, n - 2, 2 * n // 3):
            for deltas in samples:
                par = {x % 2 for x in deltas}
                if len(par) != 1:
                    continue
                # anti-values a±δ same parity as a+δ; all must match on a diagonal
                tried += 1
                rec = try_k23(n, a, deltas)
                if rec:
                    found += 1
                    print("FEASIBLE", rec, flush=True)
                    return
        print(f"n={n} no K23 yet (tried {tried})", flush=True)
    print(f"NO K_{{2,3}} in {tried} trials, found={found}", flush=True)


if __name__ == "__main__":
    main()
