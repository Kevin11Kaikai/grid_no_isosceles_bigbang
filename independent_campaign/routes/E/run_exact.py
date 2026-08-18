"""Exact C(W,H) for rectangles, seeded by local search."""
import sys, time, json, os
from iso import exact, local_search, is_iso_free

out = {}
fn = sys.argv[1] if len(sys.argv) > 1 else "exact_rect.json"
if os.path.exists(fn):
    out = json.load(open(fn))

jobs = []
maxcells = int(sys.argv[2]) if len(sys.argv) > 2 else 72
for W in range(1, 14):
    for H in range(W, 14):
        if W * H <= maxcells:
            jobs.append((W, H))
jobs.sort(key=lambda t: t[0] * t[1])

for (W, H) in jobs:
    key = f"{W}x{H}"
    if key in out:
        continue
    t = time.time()
    lb = local_search(W, H, iters=1500, restarts=6, seed=W * 100 + H)
    assert is_iso_free(lb)
    v, s = exact(W, H, seed_lb=len(lb), seed_set=lb)
    assert is_iso_free(s) and len(s) == v
    out[key] = {"val": v, "set": s, "secs": round(time.time() - t, 1)}
    print(key, v, round(time.time() - t, 1), flush=True)
    json.dump(out, open(fn, "w"))
json.dump(out, open(fn, "w"))
