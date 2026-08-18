"""Place k copies of the same two-delta S* fibre (K_{k,2} in (d,δ))."""
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


def same_parity_deltas(deltas):
    par = {x % 2 for x in deltas}
    return len(par) == 1


def try_place(n, a, deltas, k):
    if not same_parity_deltas(deltas):
        return None
    diags = []
    for d in range(1 - n, n):
        pts = fibre_points(n, a, d, deltas)
        if pts is not None:
            diags.append((d, pts))
    # greedy: add fibres while Q4-feasible
    st = FourDir(n)
    used = []
    for d, pts in diags:
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
        used.append(d)
        if len(used) >= k:
            assert verify(n, st.pts)
            return used
    return used


def main():
    configs = [
        (32, 31, (2, 8)),
        (32, 31, (1, 5)),
        (48, 47, (1, 5)),
        (48, 47, (2, 8)),
        (81, 80, (1, 5)),
        (81, 80, (2, 10)),
        (81, 81, (2, 8)),
        (128, 127, (1, 5)),
        (128, 127, (2, 8)),
        (128, 127, (1, 13)),
        (243, 242, (2, 8)),
        (243, 242, (1, 5)),
    ]
    for n, a, deltas in configs:
        for k in (2, 3, 4, 5):
            used = try_place(n, a, deltas, k)
            got = 0 if used is None else len(used)
            print(
                f"n={n:3d} a={a:3d} Δ={deltas} want_k={k} got={got}",
                flush=True,
            )
            if got < k:
                break


if __name__ == "__main__":
    main()
