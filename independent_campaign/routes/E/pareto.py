"""Core experiment: Phi(n,t) = max |S cap L| over iso-free S in [n+1]^2 with |S cap [n]^2| = t.

L = new row y=n plus new column x=n (2n+1 cells).
Traces the empirical Pareto frontier (interior size, strip size) by annealing a
weighted objective for several weights and recording every set encountered.
"""
import random, sys, json, time
from iso import State, is_iso_free
from search import force_insert


def run(n, weights, iters, seed=0, verbose=True):
    N = n + 1
    cells = [(x, y) for x in range(N) for y in range(N)]
    interior = set((x, y) for x in range(n) for y in range(n))
    frontier = {}          # t -> max strip

    def record(pts):
        t = sum(1 for p in pts if p in interior)
        s = len(pts) - t
        if frontier.get(t, -1) < s:
            frontier[t] = s

    rng = random.Random(seed)

    def refill_w(pts, w):
        st = State()
        for q in pts:
            st.add(q)
        have = set(pts)
        pool = [c for c in cells if c not in have]
        rng.shuffle(pool)
        if w != 1:   # try strip cells first when strip is valuable
            pool.sort(key=lambda c: 0 if c not in interior else 1)
        for c in pool:
            if st.can_add(c):
                st.add(c)
        return st.pts

    def val(pts, w):
        return sum((w if p not in interior else 1) for p in pts)

    for w in weights:
        cur = refill_w([], w)
        record(cur)
        for it in range(iters):
            p = cells[rng.randrange(len(cells))]
            if p in set(cur):
                continue
            cand = force_insert(cur, p, rng)
            cand = refill_w(cand, w)
            record(cand)
            d = val(cand, w) - val(cur, w)
            if d >= 0 or rng.random() < 2.718 ** (d / 0.6):
                cur = cand
        if verbose:
            print(f"  n={n} w={w} done", flush=True)
    return frontier


if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1].split(",")]
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
    out = {}
    for n in ns:
        t0 = time.time()
        fr = run(n, [1, 1.3, 2, 3, 6, 20], iters, seed=n)
        out[n] = fr
        tot = max(t + s for t, s in fr.items())
        print(f"n={n} best_total(n+1)={tot} maxstrip={max(fr.values())} "
              f"strip_at_max_t={fr[max(fr)]} maxt={max(fr)} {time.time()-t0:.0f}s", flush=True)
        print("   frontier:", " ".join(f"{t}:{s}" for t, s in sorted(fr.items()) if t >= max(fr) - 14), flush=True)
    json.dump({str(k): {str(a): b for a, b in v.items()} for k, v in out.items()},
              open(sys.argv[3] if len(sys.argv) > 3 else "pareto.json", "w"), indent=1)
