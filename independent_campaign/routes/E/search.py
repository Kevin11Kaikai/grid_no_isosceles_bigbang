"""Stronger heuristic: force-insert + repair simulated annealing."""
import random, sys, json, time
from iso import State, is_iso_free


def conflicts(pts, p):
    """Points of pts that must be removed (some hitting set) for p to be addable.
    Returns list of 'conflict pairs': each pair is a set of points, at least one
    of which must be deleted."""
    px, py = p
    d2 = [((a[0] - px) ** 2 + (a[1] - py) ** 2) for a in pts]
    cl = []
    # apex p: two old points at equal distance from p
    bydist = {}
    for i, d in enumerate(d2):
        bydist.setdefault(d, []).append(i)
    for d, idxs in bydist.items():
        if d == 0:
            cl.append((idxs[0],))
        if len(idxs) > 1:
            for a in range(len(idxs)):
                for b in range(a + 1, len(idxs)):
                    cl.append((idxs[a], idxs[b]))
    # apex b in pts: d(b,p) equals d(b,a) for some a
    for i, b in enumerate(pts):
        for j, a in enumerate(pts):
            if i == j:
                continue
            if (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 == d2[i]:
                cl.append((i, j))
    return cl


def force_insert(pts, p, rng):
    """Remove a small hitting set so that p becomes addable; return new list."""
    cl = conflicts(pts, p)
    removed = set()
    # greedy randomized hitting set
    while True:
        live = [c for c in cl if not (set(c) & removed)]
        if not live:
            break
        cnt = {}
        for c in live:
            for i in c:
                cnt[i] = cnt.get(i, 0) + 1
        mx = max(cnt.values())
        cands = [i for i, v in cnt.items() if v >= mx - 0 or (v >= mx * 0.8 and rng.random() < 0.3)]
        removed.add(rng.choice(cands))
    new = [q for i, q in enumerate(pts) if i not in removed]
    new.append(p)
    return new


def refill(pts, cells, rng):
    st = State()
    for q in pts:
        st.add(q)
    have = set(pts)
    pool = [c for c in cells if c not in have]
    rng.shuffle(pool)
    for c in pool:
        if st.can_add(c):
            st.add(c)
    return st.pts


def anneal(W, H, iters=200000, seed=0, init=None, report=None, target=None, temp=0.45):
    rng = random.Random(seed)
    cells = [(x, y) for x in range(W) for y in range(H)]
    cur = refill(list(init) if init else [], cells, rng)
    best = list(cur)
    t0 = time.time()
    for it in range(iters):
        p = cells[rng.randrange(len(cells))]
        if p in set(cur):
            continue
        cand = force_insert(cur, p, rng)
        cand = refill(cand, cells, rng)
        dlt = len(cand) - len(cur)
        if dlt >= 0 or rng.random() < 2.718 ** (dlt / temp):
            cur = cand
        if len(cur) > len(best):
            best = list(cur)
            if report:
                print(f"   [{W}x{H}] {len(best)} @it{it} {time.time()-t0:.0f}s", flush=True)
            if target and len(best) >= target:
                return best
    return best


def best_of(W, H, iters=30000, restarts=4, seed=0, target=None, report=False):
    b = []
    for r in range(restarts):
        s = anneal(W, H, iters=iters, seed=seed + 1000 * r, report=report, target=target)
        if len(s) > len(b):
            b = s
        if target and len(b) >= target:
            break
    assert is_iso_free(b)
    return b


if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1].split(",")]
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    res = {}
    for n in ns:
        t = time.time()
        s = best_of(n, n, iters=iters, restarts=3, seed=n, report=True)
        res[n] = s
        print(n, len(s), round(time.time() - t, 1), flush=True)
    json.dump({str(k): v for k, v in res.items()}, open(sys.argv[3] if len(sys.argv) > 3 else "sets.json", "w"))
