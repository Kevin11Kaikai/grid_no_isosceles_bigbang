"""Place S* K_{3,3}: three diagonals, three common same-parity deltas."""
from __future__ import annotations

from q4 import FourDir, verify
from a1_k23b import doubled_apfree, fibre, A_minus_A


def try_k33(n, a, deltas):
    if not doubled_apfree(deltas):
        return None
    forbidden = A_minus_A(a, deltas)
    diags = []
    for d in range(1 - n, n):
        pts = fibre(n, a, d, deltas)
        if pts is not None:
            diags.append((d, pts))
    st0 = FourDir(n)
    used = []
    for d, pts in diags:
        recs = []
        ok = True
        for p in pts:
            ks = st0.can_add(*p)
            if ks is None:
                ok = False
                break
            recs.append(st0.push(*p, ks))
        if not ok:
            for rec in reversed(recs):
                st0.pop(rec)
            continue
        # reject if new d differs from all used by a forbidden A-A (optional filter)
        used.append(d)
        if len(used) >= 3:
            assert verify(n, st0.pts)
            return {"n": n, "a": a, "deltas": deltas, "D": used[:3], "|pts|": len(st0.pts)}
    return {"got": len(used), "n": n, "deltas": deltas}


def main():
    samples = [
        (1, 5, 13),
        (1, 5, 17),
        (2, 8, 22),
        (1, 7, 19),
        (2, 10, 26),
        (1, 5, 25),
    ]
    for n in (32, 48, 81, 128, 243):
        for a in (n - 1, n, n - 2):
            for deltas in samples:
                if len({x % 2 for x in deltas}) != 1:
                    continue
                rec = try_k33(n, a, deltas)
                if rec and rec.get("D"):
                    print("FEASIBLE K33", rec, flush=True)
                    return
                if rec and rec.get("got", 0) >= 2:
                    print("partial", rec, flush=True)
    print("NO K_{3,3} found", flush=True)


if __name__ == "__main__":
    main()
