"""Can two S* diagonals share 3 deltas? (K_{2,3} in the (d,δ) bipartite graph)."""
from __future__ import annotations

from q4 import FourDir, verify
from lemma3_search import overlap_stats

# 3-AP-free symmetric: Δ={1,2,7} around 0 as checked by hand
DELTA = (1, 2, 7)


def points_on_diag(n, a, d, deltas):
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


def try_k23(n, a):
    hits = 0
    placed = 0
    for d1 in range(1 - n, n):
        p1 = points_on_diag(n, a, d1, DELTA)
        if p1 is None:
            continue
        for d2 in range(d1 + 2, n, 2):  # same parity
            p2 = points_on_diag(n, a, d2, DELTA)
            if p2 is None:
                continue
            hits += 1
            st = FourDir(n)
            ok = True
            for p in p1 + p2:
                ks = st.can_add(*p)
                if ks is None:
                    ok = False
                    break
                st.push(*p, ks)
            if ok:
                placed += 1
                assert verify(n, st.pts)
                return {
                    "n": n,
                    "a": a,
                    "d1": d1,
                    "d2": d2,
                    "|pts|": len(st.pts),
                    "feasible": True,
                }
    return {"n": n, "a": a, "feasible": False, "pairs_tried": hits, "placed": placed}


def main():
    for n in (16, 24, 32, 48, 81):
        for a in (n - 1, n, n - 2, 2 * n // 3, n // 2):
            rec = try_k23(n, a)
            if rec.get("feasible"):
                print("FEASIBLE", rec, flush=True)
                st = overlap_stats(n, [(0, 0)])  # dummy
                print("done", rec)
                return
            print(
                f"n={n:3d} a={a:3d} infeasible pairs_tried={rec.get('pairs_tried')}",
                flush=True,
            )
    print("NO K_{2,3} found for Δ={1,2,7}", flush=True)


if __name__ == "__main__":
    main()
