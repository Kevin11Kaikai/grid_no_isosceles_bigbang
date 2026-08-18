"""Independent re-validation of route E's primitives.

1. brute_check: O(|S|^3) triple enumeration, written from scratch (ground truth).
2. cross-check against iso.is_iso_free and iso.State.can_add on random sets.
3. independent exact solver (bitset/greedy-order DFS) cross-checked against iso.exact.
4. re-verify every stored exact_rect.json optimum is iso-free and matches sealed values.
"""
import json, random, itertools, sys, time
from iso import is_iso_free, State, exact


def brute_check(S):
    """True iff no three DISTINCT a,b,c in S with d(a,b)=d(b,c). Ground truth."""
    S = list(S)
    if len(set(S)) != len(S):
        return False
    n = len(S)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if i == j or j == k or i == k:
                    continue
                a, b, c = S[i], S[j], S[k]
                d1 = (a[0]-b[0])**2 + (a[1]-b[1])**2
                d2 = (c[0]-b[0])**2 + (c[1]-b[1])**2
                if d1 == d2:
                    return False
    return True


def cross_check_verifier(trials=4000, seed=0):
    rng = random.Random(seed)
    bad = 0
    for t in range(trials):
        n = rng.randint(2, 8)
        m = rng.randint(3, 7)
        pts = rng.sample([(x, y) for x in range(n) for y in range(n)], k=min(m, n*n))
        a, b = brute_check(pts), is_iso_free(pts)
        if a != b:
            bad += 1
            print("MISMATCH", pts, a, b)
        # State.can_add consistency: build incrementally
        st = State()
        ok = True
        for p in pts:
            if not st.can_add(p):
                ok = False
                break
            st.add(p)
        if ok != a:
            bad += 1
            print("CANADD MISMATCH", pts, a, ok)
    return bad


def exact2(W, H):
    """Independent exact max: DFS over cells in a different (row-major) order,
    no seeding, simple bound.  Slow but structurally different from iso.exact."""
    cells = [(x, y) for y in range(H) for x in range(W)]
    N = len(cells)
    best = [0]
    cur = []

    def ok(p):
        for i, b in enumerate(cur):
            d = (p[0]-b[0])**2 + (p[1]-b[1])**2
            if d == 0:
                return False
        # apex p
        ds = set()
        for b in cur:
            d = (p[0]-b[0])**2 + (p[1]-b[1])**2
            if d in ds:
                return False
            ds.add(d)
        # apex b in cur
        for b in cur:
            d = (p[0]-b[0])**2 + (p[1]-b[1])**2
            for a in cur:
                if a is b:
                    continue
                if (a[0]-b[0])**2 + (a[1]-b[1])**2 == d:
                    return False
        return True

    def rec(i):
        if len(cur) + (N - i) <= best[0]:
            return
        if i == N:
            if len(cur) > best[0]:
                best[0] = len(cur)
            return
        p = cells[i]
        if ok(p):
            cur.append(p)
            rec(i+1)
            cur.pop()
        rec(i+1)

    rec(0)
    return best[0]


if __name__ == "__main__":
    t0 = time.time()
    bad = cross_check_verifier()
    print(f"verifier cross-check: {bad} mismatches in 4000 random sets  ({time.time()-t0:.1f}s)")

    # stored optima
    d = json.load(open("exact_rect.json"))
    sealed_sq = {1: 1, 2: 2, 3: 4, 4: 6, 5: 7, 6: 9, 7: 10, 8: 13, 9: 16, 10: 18, 11: 18}
    nbad = 0
    for k, v in d.items():
        S = [tuple(p) for p in v["set"]]
        assert len(S) == v["val"], k
        if not brute_check(S):
            print("STORED SET NOT ISO-FREE", k); nbad += 1
        W, H = map(int, k.split("x"))
        for (x, y) in S:
            assert 0 <= x < W and 0 <= y < H, (k, x, y)
    print(f"all {len(d)} stored optimal sets verified iso-free & in-box ({nbad} bad)")
    for n, c in sealed_sq.items():
        k = f"{n}x{n}"
        if k in d:
            print(f"  C({n}) stored={d[k]['val']}  sealed={c}  {'OK' if d[k]['val']==c else 'MISMATCH'}")

    # independent exact solver on small boxes
    print("independent exact2 vs iso.exact:")
    for W in range(1, 6):
        for H in range(W, 7):
            if W*H > 26:
                continue
            v1 = exact2(W, H)
            v2, _ = exact(W, H)
            st = d.get(f"{W}x{H}", {}).get("val")
            print(f"  {W}x{H}: exact2={v1} iso.exact={v2} stored={st} "
                  f"{'OK' if v1 == v2 and (st is None or st == v1) else 'MISMATCH'}")
