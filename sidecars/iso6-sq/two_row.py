"""F_2(n): max square-corner-free set on two rows of [n]^2.

Enumerate n<=8. Check equality construction. No battery.
"""
from __future__ import annotations

import json
from pathlib import Path

from sq import is_sq_free

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)


def bits(mask, n):
    return [i for i in range(n) if mask >> i & 1]


def two_row_pts(n, d, A, B, y=0):
    return [(x, y) for x in A] + [(z, y + d) for z in B]


def combo_sq_free(n, d, A, B):
    """Plan classification: vertical + diagonal. A,B as sets."""
    I = A & B
    U = A | B
    for x in I:
        for t in (x + d, x - d):
            if 0 <= t < n and t in U:
                return False
    for x in A:
        if (x - d) in B and (x + d) in B:
            return False
    for x in B:
        if (x - d) in A and (x + d) in A:
            return False
    return True


def enum_n(n):
    n_masks = 1 << n
    best = 0
    best_ex = None
    n_combo_ok = 0
    n_iso = 0
    mismatch = 0
    for d in range(1, n):
        for ma in range(n_masks):
            A = set(bits(ma, n))
            for mb in range(n_masks):
                B = set(bits(mb, n))
                sz = len(A) + len(B)
                ok_c = combo_sq_free(n, d, A, B)
                if ok_c:
                    n_combo_ok += 1
                pts = two_row_pts(n, d, A, B)
                ok_s = is_sq_free(pts)
                if ok_s:
                    n_iso += 1
                if ok_c != ok_s:
                    mismatch += 1
                    if mismatch <= 3:
                        return {
                            "n": n,
                            "mismatch": True,
                            "d": d,
                            "A": sorted(A),
                            "B": sorted(B),
                            "combo": ok_c,
                            "is_sq_free": ok_s,
                        }
                if ok_s and sz > best:
                    best = sz
                    best_ex = {"d": d, "A": sorted(A), "B": sorted(B), "|S|": sz}
    return {
        "n": n,
        "F_2": best,
        "2n-2": 2 * n - 2,
        "match_2n-2": best == 2 * n - 2,
        "best": best_ex,
        "n_combo_ok": n_combo_ok,
        "n_is_sq_free": n_iso,
        "mismatch": False,
    }


def equality_pts(n, which="left"):
    d = n - 1
    if which == "left":
        I = list(range(n - 1))  # {0,...,n-2}
    else:
        I = list(range(1, n))
    return n, d, two_row_pts(n, d, I, I)


def main():
    rows = []
    for n in range(2, 9):
        rec = enum_n(n)
        rows.append(rec)
        print(rec, flush=True)
        if rec.get("mismatch"):
            break

    eq = []
    for n in [3, 4, 5, 8, 16, 32, 48, 64]:
        for which in ("left", "right"):
            nn, d, pts = equality_pts(n, which)
            ok = is_sq_free(pts)
            eq.append(
                {
                    "n": n,
                    "which": which,
                    "|S|": len(pts),
                    "2n-2": 2 * n - 2,
                    "sq_free": ok,
                }
            )
            print(f"eq n={n} {which} |S|={len(pts)} sq_free={ok}", flush=True)

    out = {"enum": rows, "equality": eq}
    p = OUT / "two_row.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", p, flush=True)


if __name__ == "__main__":
    main()
