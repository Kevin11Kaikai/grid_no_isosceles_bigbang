"""Forbidden-strip-cell census.

For S0 iso-free inside [n]^2 and the new row R = {(x,n) : 0<=x<=n}, a cell p=(x,n)
is individually forbidden by exactly one of:

 (C2) apex at p : exists b != b' in S0 with |p-b| = |p-b'|.
      For b,b' in DIFFERENT columns this pins x to a single rational value
          x = (h'^2+g'-h^2-g) / (2(h'-h)),  h=b1, g=(n-b2)^2.
      For b,b' in the SAME column it is impossible.  -> "bisector" constraint
 (C3) apex at b in S0 : exists a in S0 with |p-b| = |a-b|.
      (x-b1)^2 = |a-b|^2 - (n-b2)^2 must be a perfect square. -> "shell" constraint

 (C1) apex at b in S0, two strip points p,p' : x+x' = 2*b1.  This is a constraint on
      PAIRS of surviving cells, not on single cells: the surviving set T must have
      its integer midpoint set disjoint from pi_1(S0).
"""
import sys, json, random, time
from fractions import Fraction
from iso import State, is_iso_free
from search import best_of


def census(S0, n):
    R = list(range(n + 1))                     # x-coords of new row cells
    t = len(S0)
    # ---- C2 : bisector hits
    bad2 = set()
    mult2 = {}
    pts = [(b[0], (n - b[1]) ** 2) for b in S0]
    for i in range(t):
        h, g = pts[i]
        for j in range(i + 1, t):
            h2, g2 = pts[j]
            if h == h2:
                continue                        # same column: never forbids
            num = h2 * h2 + g2 - h * h - g
            den = 2 * (h2 - h)
            if num % den == 0:
                x = num // den
                if 0 <= x <= n:
                    bad2.add(x)
                    mult2[x] = mult2.get(x, 0) + 1
    # ---- C3 : distance-shell hits
    bad3 = set()
    mult3 = {}
    for b in S0:
        b1, b2 = b
        v = (n - b2) ** 2
        for a in S0:
            if a == b:
                continue
            q = (a[0] - b1) ** 2 + (a[1] - b2) ** 2 - v
            if q < 0:
                continue
            r = int(q ** 0.5)
            while r * r < q:
                r += 1
            while r * r > q:
                r -= 1
            if r * r != q:
                continue
            for x in (b1 - r, b1 + r):
                if 0 <= x <= n:
                    bad3.add(x)
                    mult3[x] = mult3.get(x, 0) + 1
    surv = [x for x in R if x not in bad2 and x not in bad3]
    # cross-check against the brute-force incremental test
    st = State()
    for p in S0:
        st.add(p)
    surv_bf = [x for x in R if st.can_add((x, n))]
    assert surv == surv_bf, (surv, surv_bf)
    X = set(b[0] for b in S0)
    return dict(n=n, t=t, row=n + 1,
                c2=len(bad2), c3=len(bad3), only2=len(bad2 - bad3),
                only3=len(bad3 - bad2), both=len(bad2 & bad3),
                surv=len(surv), survset=surv,
                maxmult2=max(mult2.values()) if mult2 else 0,
                avgmult2=round(sum(mult2.values()) / max(1, len(mult2)), 1),
                pairs=t * (t - 1) // 2, k=len(X),
                lemma_bound=n + 4 - len(X))


def random_subsets(S, sizes, rng):
    """Iso-free subsets of S of prescribed sizes (subsets of iso-free sets are iso-free)."""
    out = {}
    for s in sizes:
        if s <= len(S):
            out[s] = rng.sample(S, s)
    return out


if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1].split(",")]
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
    rng = random.Random(7)
    res = []
    for n in ns:
        S = best_of(n, n, iters=iters, restarts=2, seed=n)
        print(f"n={n} near-extremal |S0|={len(S)}", flush=True)
        sizes = sorted(set([1, 2, 3, 5, 8] + [int(len(S) * f) for f in (.2, .4, .6, .8, .9, 1.0)]))
        subs = random_subsets(S, sizes, rng)
        for s, sub in sorted(subs.items()):
            c = census(sub, n)
            c.pop("survset")
            res.append(c)
            print("   ", c, flush=True)
    json.dump(res, open(sys.argv[3] if len(sys.argv) > 3 else "forbid.json", "w"), indent=1)
