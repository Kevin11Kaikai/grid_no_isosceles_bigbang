"""Driver: run the exact / heuristic solvers, verify every set, archive it."""
import os, re, subprocess, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify import is_isofree, witnesses

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SETS = os.path.join(ROOT, "routes", "C", "sets")
os.makedirs(SETS, exist_ok=True)
EXACT = os.path.join(HERE, "exact2.exe")
HEUR = os.path.join(HERE, "heur.exe")


def parse(out):
    opt, pts = None, None
    for line in out.splitlines():
        m = re.match(r"BOARD (\d+)x(\d+)\s+OPT (\d+)", line)
        if m:
            opt = int(m.group(3))
        m = re.match(r"BOARD (\d+)x(\d+) BEST (\d+)", line)
        if m:
            opt = int(m.group(3))
        if line.startswith("SET"):
            pts = [tuple(map(int, t.split(","))) for t in line.split()[1:]]
    return opt, pts


def save(w, h, pts, tag, exact):
    assert is_isofree(pts), ("SET FAILED VERIFICATION", w, h, pts)
    fn = os.path.join(SETS, "%s_%dx%d_k%d.txt" % (tag, w, h, len(pts)))
    with open(fn, "w") as f:
        f.write("# board %d x %d, |S| = %d, %s\n" %
                (w, h, len(pts), "EXHAUSTIVE OPTIMUM" if exact else "best found (lower bound)"))
        for (x, y) in sorted(pts, key=lambda p: (p[1], p[0])):
            f.write("%d %d\n" % (x, y))
    return fn


def run_exact(w, h, lb=0, threads=8, td=3, timeout=None):
    r = subprocess.run([EXACT, str(w), str(h), str(lb), str(threads), str(td)],
                       capture_output=True, text=True, timeout=timeout)
    opt, pts = parse(r.stdout)
    if pts:
        assert is_isofree(pts), ("EXACT SET FAILED VERIFICATION", w, h, pts)
        save(w, h, pts, "exact", True)
    return opt, pts, r.stdout


def run_heur(w, h, k0=1, secs=10, seed=1):
    r = subprocess.run([HEUR, str(w), str(h), str(k0), str(secs), str(seed)],
                       capture_output=True, text=True)
    opt, pts = parse(r.stdout)
    if pts:
        assert is_isofree(pts), ("HEUR SET FAILED VERIFICATION", w, h, pts)
    return opt, pts


if __name__ == "__main__":
    pass
