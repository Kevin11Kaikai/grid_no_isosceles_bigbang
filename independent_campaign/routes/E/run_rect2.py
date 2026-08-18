"""Exact R(W,H) for narrow rectangles: the anisotropic increment data.

R(W,H) = max iso-free subset of {0..W-1} x {0..H-1}.
We grow H with W fixed, which is the 'grow one dimension at a time' induction.
Seeded by local search + previous R(W,H-1) as a lower bound is NOT valid as a
seed for optimality (R is monotone in H so R(W,H) >= R(W,H-1) IS valid).
"""
import sys, time, json, os
from iso import exact, local_search, is_iso_free

fn = sys.argv[1] if len(sys.argv) > 1 else "rect2.json"
out = json.load(open(fn)) if os.path.exists(fn) else {}
# merge in the earlier table
if os.path.exists("exact_rect.json"):
    for k, v in json.load(open("exact_rect.json")).items():
        out.setdefault(k, v)

Wmax = int(sys.argv[2]) if len(sys.argv) > 2 else 5
Hmax = int(sys.argv[3]) if len(sys.argv) > 3 else 22
budget = float(sys.argv[4]) if len(sys.argv) > 4 else 3600.0

t_start = time.time()
for W in range(1, Wmax + 1):
    for H in range(W, Hmax + 1):
        key = f"{W}x{H}" if W <= H else f"{H}x{W}"
        if key in out:
            continue
        if time.time() - t_start > budget:
            print("budget exhausted", flush=True)
            sys.exit(0)
        t = time.time()
        prev = out.get(f"{W}x{H-1}")
        lbset = local_search(W, H, iters=1200, restarts=6, seed=W * 100 + H)
        if prev and prev.get("set") and len(prev["set"]) > len(lbset):
            lbset = [tuple(p) for p in prev["set"]]      # subset of the taller box
        assert is_iso_free(lbset)
        v, s = exact(W, H, seed_lb=len(lbset), seed_set=lbset)
        assert is_iso_free(s) and len(s) == v
        out[key] = {"val": v, "set": s, "secs": round(time.time() - t, 1)}
        print(key, v, round(time.time() - t, 1), flush=True)
        json.dump(out, open(fn, "w"))
json.dump(out, open(fn, "w"))
print("done")
